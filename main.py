from environment import Environment
from agents import SimpleAgent, DijkstraAgent, InteractiveDijkstraAgent, Messenger, ACKMessage, GiveWayMessage
from displayer import Application
from PIL import Image, ImageTk

N = 5

if __name__ == '__main__':
    env = Environment(N)
    for i in range(7):
        #env.add_agent(SimpleAgent(i, env.generate_random_position(), i, env))
        env.add_agent(DijkstraAgent(i, env.generate_random_position(), i, env))
        #env.add_agent(InteractiveDijkstraAgent(i, env.generate_random_position(), i, env))

    app = Application(env)
    env.start_agent()
    app.mainloop()

# for i in range(0, 17):
#     im = Image.open("images/4x4/"+str(i)+".png")
#     im2 = im.resize((125,125))
#     im2.save(str(i)+".png")
