from environment import Environment
from agents import SimpleAgent, DijkstraAgent, InteractiveDijkstraAgent, Messenger, ACKMessage, GiveWayMessage

N = 5

if __name__ == '__main__':
    env = Environment(N)
    for i in range(10):
        # env.add_agent(SimpleAgent(i, env.generate_random_position(), i, env))
        # env.add_agent(DijkstraAgent(i, env.generate_random_position(), i, env))
        env.add_agent(InteractiveDijkstraAgent(i, env.generate_random_position(), i, env))

    env.start_agent()
    while not env.is_finish():
        if env.update:
            print(env)
            env.update = False
    print(env)
