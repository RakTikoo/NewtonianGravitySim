from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.trail_renderer import TrailRenderer

import math


G_const = 10

class LargeBody(Entity):
    LargeBodies = []
    mass = 1
    velocity = Vec3(0, 0)
    destroy = 0
    paused = 1

    def __init__(self, position=Vec3(0, 0, 0), mass = 1, velocity = Vec3(0, 0, 0), scale = 1, color = color.red, paused = 1, **kwargs):
        super().__init__(model = "sphere", color = color, collider = "box", position = position, parent=scene, texture = "white_cube", scale = scale)  #Why does this work? Don't understand --> only in orthographic view
        self.paused = paused
        self.mass = mass
        self.velocity = velocity
        TrailRenderer(parent = self, size=[0.1,0.1], segments=75)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def setLargeBodies(self, newBody):
        #self.LargeBodies += [newBody]
        self.LargeBodies = newBody
        #print(self.LargeBodies)

    def calcDistance(self, pos1, pos2):
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)


    def update(self): 
        global G_const
        if self.paused == 0:
            #Calculate net force
            NetForce = Vec3(0, 0, 0)
            #temp = self.LargeBodies[:]
            for Body in self.LargeBodies:
                    dist = self.calcDistance(self.position, Body.position)
                    if dist != 0:
                        scalar = (G_const*Body.mass*self.mass)/(dist**2)
                        vect = (Body.position - self.position)/dist
                        currForce = scalar*vect
                        NetForce += currForce


                    if self.intersects(Body):
                        if self.destroy == 0:
                            Body.destroy = 1
                        self.position = (self.mass*self.position + Body.mass*Body.position)/(self.mass + Body.mass)
                        self.velocity = (self.mass*self.velocity + Body.mass*Body.velocity)/(self.mass + Body.mass)
                        self.mass += Body.mass
                        self.scale = max(Body.scale, self.scale)*((Body.mass/self.mass) + 1)
                        self.color = (self.color + Body.color)*0.5
                        #self.combine(Body)
                        #self.LargeBodies.remove(Body)




            netAccel = NetForce/self.mass
            self.velocity += netAccel*time.dt
            self.position += self.velocity*time.dt


        #Bound Check
        #print(window.size.x , window.size.y)
        #print(self.position.x, self.position.y)
        if abs(self.position.x) > window.size.x or abs(self.position.y) > window.size.y:
            #print("OK")
            self.destroy = 1


        if self.destroy == 1:
            self.LargeBodies.remove(self)
            destroy(self)

            
        




if __name__ == '__main__':
    app = Ursina()

    Entities = []
    paused = 1
    #Intialize UI
    Text(text="Mass", x=1.0, y = 0.25)
    mass_field = InputField(default_value='1', label='', max_lines=1, character_limit=10,  x=1.085, y = 0.2, scale_y = 0.05, scale_z = 0.05, scale_x = 0.185)

    Text(text="Velocity", x=1.0, y = 0.0)
    vel_field = InputField(default_value='0 0 0', label='', max_lines=1, character_limit=10,  x=1.085, y = -0.05, scale_y = 0.05, scale_z = 0.05, scale_x = 0.185)

    pause_text = Text(text="Paused", x=1.0, y = -0.25)
    #color_field = InputField(default_value='1 0 0', label='', max_lines=1, character_limit=10,  x=1.085, y = -0.3, scale_y = 0.05, scale_z = 0.05, scale_x = 0.185)
    

    def input(key):
        global Entities
        global paused
        if key == "p":
            if paused == 1:
                paused = 0
                pause_text.text = ""
            else:
                paused = 1
                pause_text.text = "Paused"

            for Entity in Entities:
                Entity.paused = paused


        if key == 'q':
            #print("Added Entity")
            screen_mouse_position = mouse.position*Ecamera.target_fov
            mass = 1
            scale = mass
            velocity = Vec3(0, 0, 0)
            color_ = color.random_color()

            if mass_field.text != "":
                mass = float(mass_field.text)
                scale = 10*max(math.log10(mass), 0.1)
            
            if vel_field.text != "":
                temp = vel_field.text.split()
                velocity = Vec3(float(temp[0]), float(temp[1]), float(temp[2]))

            #if color_field.text != "":
            #    temp = color_field.text.split()
            #    color = Vec3(float(temp[0]), float(temp[1]), float(temp[2]))


            new_Entity = LargeBody(
            position=screen_mouse_position, mass = mass, velocity = velocity, scale = scale, color = color_, paused = paused
            )

            Entities += [new_Entity]

            for Entity in Entities:
                Entity.setLargeBodies(Entities)
        
            #print(camera.position)
            #print(Ecamera.perspective_fov)
            #print(Ecamera.orthographic_fov)
            #print(Ecamera.start_position)
            #print(camera.ui)
            #print(camera.ui_size)
            #print(Ecamera.target_fov)
            #print(window.size)
            #print(mouse.position)


        #Delete All
        if key == "d":
            temp = Entities[:]
            for Entity in temp:
                Entity.destroy = 1

        #Reset camera position
        if key == "r":
            Ecamera.world_position = Vec3(0, 0, 0)
            Ecamera.rotation = Vec3(0, 0, 0)
        
        
            

        

            
    
    camera.orthographic = True
    Ecamera = EditorCamera()
    #camera.position_setter((0, 0, -20))
    app.run()