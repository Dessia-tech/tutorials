from tutorials.simple_bearing import Ball, Bearing

ball = Ball(0.5, name='test1')
bearing = Bearing(ball, 5, 6, 0.5,
                  thickness=0.1, name='test2')

bearing.display_2d(pos_x=2, pos_y=3, number_balls=20).plot()
bearing.babylonjs()
