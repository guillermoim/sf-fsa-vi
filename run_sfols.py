from fsa.planning import SFFSAValueIteration as ValueIteration
from sfols.rl.utils.utils import policy_eval_exact
from sfols.rl.successor_features.gpi import GPI
from sfols.rl.successor_features.ols import OLS
from fsa.tasks_specification import load_fsa
from omegaconf import DictConfig, OmegaConf
from envs.wrappers import GridEnvWrapper

from utils.utils import seed_everything 

import pickle as pkl
import numpy as np
import wandb as wb
import shutil
import hydra
import envs
import gym
import os


@hydra.main(version_base=None, config_path="conf", config_name="default")
def main(cfg: DictConfig) -> None:
    
    # Init Wandb
    run = wb.init(
        config=OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True),
        entity=cfg.wandb.entity, project=cfg.wandb.project,
        group="sfols", tags=["sfols"],
        # mode = "disabled"

    )
    run.tags = run.tags 
    
    # Set seeds
    seed_everything(cfg.seed)

    # Create the train and eval environments
    env_params = dict(cfg.env)
    env_name = env_params.pop("env_name")
    train_env = gym.make(env_name, add_obj_to_start=True)
    eval_env = gym.make(env_name)

    # Create the FSA env wrapper, to evaluate the FSA
    fsa, T = load_fsa('-'.join([env_name, cfg.fsa_name]), eval_env) # Load FSA
    eval_env = GridEnvWrapper(eval_env, fsa, fsa_init_state="u0", T=T)


    # Define the agent constructor and gpi agent
    def agent_constructor(log_prefix: str):
        return hydra.utils.call(config=cfg.algorithm, env=train_env, log_prefix=log_prefix, fsa_env=eval_env)

    gpi_agent = GPI(train_env,
                    agent_constructor,
                    **cfg.gpi.init,
                    planning_constraint=cfg.env.planning_constraint)

    # m = number of predicates
    # Need to add the constraint, which sets add some restriction to the extrema weights.
    ols = OLS(m=train_env.feat_dim, **cfg.ols, restriction=cfg.env.restriction)

    # Directory for storing the policies
    directory = train_env.unwrapped.spec.id
    shutil.rmtree(f"results/sfols/policies/{directory}", ignore_errors=True)
    os.makedirs(f"results/sfols/policies/{directory}", exist_ok=True)

    for ols_iter in range(cfg.max_iter_ols):
        
        if ols.ended():
            print("ended at iteration", ols_iter)
            break
       
        w = ols.next_w()
        print(f"Training {w}")

        gpi_agent.learn(w=w, reuse_value_ind=ols.get_set_max_policy_index(w), **cfg.gpi.learn)
        value = policy_eval_exact(agent=gpi_agent, env=train_env, w=w) # Do the expectation analytically
        remove_policies = ols.add_solution(value, w, gpi_agent=gpi_agent, env=train_env)
        gpi_agent.delete_policies(remove_policies)


    for i, pi in enumerate(gpi_agent.policies):
        d = vars(pi)
        d.pop("replay_buffer")
        d.pop("env")
        d.pop("gpi")
        with open(f"results/sfols/policies/{train_env.unwrapped.spec.id}/discovered_policy_{i + 1}.pkl", "wb") as fp:
            pkl.dump(d, fp)
        wb.save(f"results/sfols/policies/{train_env.unwrapped.spec.id}/discovered_policy_{i + 1}.pkl")

        run.summary["policies_obtained"] = len(gpi_agent.policies)


    # Once the low-level policies have been obtained we can retrain the high-level 
    # policy and keep track of the results.

    wb.define_metric("evaluation/acc_reward", step_metric="evaluation/iter")


    planning = ValueIteration(eval_env, gpi_agent, constraint=cfg.env.planning_constraint)
    W = None

    times = []

    for j in range(50):

        W, time = planning.traverse(W, num_iters = 1)
        times.append(time)
        rewards = []
        for _ in range(gpi_agent.eval_episodes):
            acc_reward = gpi_agent.evaluate(gpi_agent, eval_env, W)
            rewards.append(acc_reward)
            
        log_dict = {"evaluation/acc_reward": np.average(rewards),
                    "evaluation/iter": j,
                    "evaluation/time": np.sum(times)}
        
        wb.log(log_dict)


    wb.finish()



if __name__ == "__main__":
    main()
