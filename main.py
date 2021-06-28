from environment import Environment
from agents import SimpleAgent, DijkstraAgent, InteractiveAgent, Messenger, ACKMessage, GiveWayMessage
from displayer import Application
from PIL import Image, ImageTk

N = 4
#
if __name__ == '__main__':
    env = Environment(N)
    for i in range(N*N-1):
        # env.add_agent(SimpleAgent(i, env.generate_random_position(), i, env))
        #env.add_agent(DijkstraAgent(i, env.generate_random_position(), i, env))
        env.add_agent(InteractiveAgent(i, env.generate_random_position(), i, env))

    app = Application(env)
    env.start_agent()
    app.mainloop()



