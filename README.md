# Breakout
Breakout Game By Yash Agarwal
In this I will go by steps what I did
So firstly my thought was to just create a basic breakout game, once I did that with very minmal physics such as just going opposite directions
I decided to implement AI to it
Here is where it got hard as I had to first decide on what kind of AI I will be using, therefore after a lot of research and implementation
I found out reinforcement learning with q table would be great
so I implemented a action function shich chooses action based on epsilon greedy policy and a q table based on q learning algorithm and a get reward function
but it was not very good as it lost most of the time it is still there which I can use, if anytime found better solutions
but later i applied reward function on scored which made it better but still was very bad overall
after that i just implemented how to track the ball and the paddle moving according to the ball's location which makes it almost impossible to lose the game
Later on i started to change game physics by a little such as using random module to make angles randon when it hits the bricks or walls and had a tought time
as it broke the code many times and it took me days and hours to fix it.
After fixing all of that i saw pymunk module which uses a lot more physics and tried to incorporate it which again had a lot of problems and still it is buggy but
playable, like when colliding with wall edges and bricks are weird in visual.
after that I noticed that if I increase the speed of the all the paddle was not able to keep with it so I had to increase the speed of the paddle.
Later on i decided to game look as better as I can in the time left so i used the pygame gfxdraw module, which made the bricks and paddle look better but
the ball is still pretty bad as I could not debug the code in time after I changed the graphics of the ball
The project took a lot of research, and there was a lot of data on it online, but it was fun and I am very excited to see how I implemented something which I always dreamt of I will continue working on this project and try to make new things in the game and implement new AI algorithms into it and see how it works
