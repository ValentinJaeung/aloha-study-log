from dm_control import viewer
from sim_env import make_sim_env
env=make_sim_env('sim_transfer_cube_scripted')
viewer.launch(env)