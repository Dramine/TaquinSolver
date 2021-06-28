from environment import Environment
from agents import SimpleAgent, DijkstraAgent, InteractiveAgent, Messenger, ACKMessage, GiveWayMessage, Message

N = 5

if __name__ == '__main__':
    m1 = Messenger(1)
    m2 = Messenger(2)

    env = Environment(N)
    # env.add_agent(InteractiveAgent(0, 0, 0, env))
    # env.add_agent(InteractiveAgent(1, 1, 1, env))
    for i in range(N*N-1):
        # env.add_agent(SimpleAgent(i, env.generate_random_position(), i, env))
        # env.add_agent(DijkstraAgent(i, env.generate_random_position(), i, env))
        env.add_agent(InteractiveAgent(i, env.generate_random_position(), i, env))

    env.start_agent()
    print(env)
    while not env.is_finish():
        if env.update:
            print(env)
            env.update = False
    print(env)
