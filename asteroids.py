import pygame as pg
import random
import math
pg.init()

background_clr = (0,0,0)
asteroid_clr = (255,255,255)
ship_clr = (255,255,0)
bullet_clr = (255,0,0)
laser_clr = (255,100,0)
bar1_clr = (255,0,0)
bar2_clr = (0,255,0)
shootspeed_clr = (255,0,255)

font1 = pg.font.SysFont("Calibri",40)
font2 = pg.font.SysFont("Calibri",20)

displaysize = (800,600)
clockspeed = 100
endless_mode = True
aimbot = False
upgrade_chance = 0.3

asteroid_thickness = 1
asteroid_radius = 30
asteroid_points = 19
asteroid_deviation = 0.1
asteroid_rotation_angle = math.pi/100
asteroid_speed = 1
max_asteroids = 4
asteroid_tiers = 2
asteroid_offsprings = 3

ship_speed = 1.5
ship_accelleration = 0.02
ship_rot_speed = math.pi/100
ship_scale = 20
drag_coefficient = 0.002
shoot_cooldown = 80
enable_reverse = True

bullet_speed = 8
bullet_length = 12
bullet_thickness = 4

laser_reduction = 0.02

upgrade_radius = 10
shootspeed_duration = 800



def calculate_velocities(speed, angle_radians):

    x_velocity = speed * math.cos(angle_radians)
    y_velocity = speed * math.sin(angle_radians)
    
    return x_velocity, y_velocity


def distance_point_to_line(G, A, B):
    # Calculate the direction vector of the line segment AB
    AB = (B[0] - A[0], B[1] - A[1])
    
    # Calculate the vector from A to G
    AG = (G[0] - A[0], G[1] - A[1])
    
    # Calculate the length of the line segment AB
    length_AB = math.sqrt(AB[0] ** 2 + AB[1] ** 2)
    
    # Calculate the dot product of AG and AB
    dot_product = AG[0] * AB[0] + AG[1] * AB[1]
    
    # Calculate the projection of AG onto AB
    projection = (dot_product / (length_AB ** 2)) * AB[0], (dot_product / (length_AB ** 2)) * AB[1]
    
    # Calculate the vector from G to the projection point on AB
    GP = (AG[0] - projection[0], AG[1] - projection[1])
    
    # Calculate the distance between point G and the line AB
    distance = math.sqrt(GP[0] ** 2 + GP[1] ** 2)
    
    return distance

def generate_asteroid(radius, num_points=12, deviation=0.2):
    # Generate points for a circle
    circle_points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        circle_points.append((x, y))

    # Modify the points to create an asteroid-like shape
    asteroid_points = []
    for x, y in circle_points:
        # Add random deviation to the radius
        r = radius + random.uniform(-deviation * radius, deviation * radius)
        
        # Create the asteroid shape by applying a random angle to each point
        angle = math.atan2(y, x)
        angle += random.uniform(-deviation * math.pi, deviation * math.pi)
        new_x = r * math.cos(angle)
        new_y = r * math.sin(angle)
        asteroid_points.append((new_x, new_y))

    return list(asteroid_points)




class asteroid_class:
    def __init__(self,pos,R,P,D,tier):
        self.basepoints = generate_asteroid(R,P,D)
        self.x,self.y = pos
        self.radius = R
        self.tier = tier
        self.xvel,self.yvel = calculate_velocities(asteroid_speed,random.random()*(math.pi*2))


        self.points = [(x + self.x, y + self.y) for x, y in self.basepoints]


    def rotate_self(self, angle_in_radians):

        cos_angle = math.cos(angle_in_radians)
        sin_angle = math.sin(angle_in_radians)

        for i, point in enumerate(self.basepoints):
            x, y = point

            new_x = x * cos_angle - y * sin_angle
            new_y = x * sin_angle + y * cos_angle

            self.basepoints[i] = (new_x, new_y)
            

        
    def draw_self(self):
        pg.draw.polygon(display, asteroid_clr, self.points, asteroid_thickness)
        if debug:
            pg.draw.circle(display,(255,255,255),(self.x,self.y),2)
            text = font.render(str(round(self.x))+", "+str(round(self.y)),True,(255,255,255))
            display.blit(text,(self.x+self.radius,self.y+self.radius))


    def move_self(self):
        self.x += self.xvel
        self.y += self.yvel


        if self.x < -self.radius:
            self.x = displaysize[0]+self.radius
#            self.y = displaysize[1] - self.y

        if self.x > displaysize[0]+self.radius:
            self.x = -self.radius
#            self.y = displaysize[1] - self.y

        if self.y < -self.radius:
            self.y = displaysize[1]+self.radius
#            self.x = displaysize[0] - self.x

        if self.y > displaysize[1]+self.radius:
            self.y = -self.radius
#            self.x = displaysize[0] - self.x

        self.points = [(x + self.x, y + self.y) for x, y in self.basepoints]




    def collide_self(self):
        global bullets,asteroids
        for bullet in bullets:
            if type(bullet) == bullet_class:
                bullet_point1 = bullet.points[0]
                bullet_point2 = bullet.points[1]
                
                distance = math.sqrt((self.x - bullet_point1[0])**2 + (self.y - bullet_point1[1])**2)
            if type(bullet) == laser_class:
                distance = distance_point_to_line((self.x,self.y), bullet.start, bullet.end)
            
            if distance <= self.radius:
                try:
                    if self.tier > 1:
                        self.shatter_self()
                        asteroids.remove(self)
                    else:
                        asteroids.remove(self)
                        spawn_upgrades((self.x,self.y))
                        if endless_mode and len(asteroids) < max_asteroids:
                            asteroids.append(asteroid_class([0,random.randint(0,displaysize[1])],asteroid_radius,asteroid_points,asteroid_deviation,asteroid_tiers))
                    if type(bullet) == bullet_class:
                        bullets.remove(bullet)
                except:
                    print("Non-fatal error during  collision detection.")


    def shatter_self(self):
        global asteroids
        new_radius = self.radius - (asteroid_radius/asteroid_tiers)
        for i in range(asteroid_offsprings):
             asteroids.append(asteroid_class([self.x,self.y],new_radius,asteroid_points,asteroid_deviation,self.tier-1))
    

      

class ship_class:
    def __init__(self):
        self.x,self.y = displaysize[0]/2,displaysize[1]/2
        self.angle = 0
        self.basepoints = [(0.5,0),(1,1),(0.5,0.7),(0,1)]
        self.points = [(x*ship_scale+(self.x-ship_scale),y*ship_scale+(self.y-ship_scale)) for x,y in self.basepoints]
        self.accelleration = 0
        self.xvel,self.yvel = 0,0
        self.sel_weapon = 0
        self.cooldown = [0,shoot_cooldown]
        self.laser_cooldown = [0,shoot_cooldown*10]



    def calculate_rotated_points(self):

        cos_angle = math.cos(self.angle)
        sin_angle = math.sin(self.angle)
        
        rotated_points = [(x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle) for x, y in [(x - 0.5, y - 0.5) for x, y in self.basepoints]]
        scaled_points = [(x * ship_scale + self.x, y * ship_scale + self.y) for x, y in rotated_points]
        
        return scaled_points

    
    def draw_self(self):
        self.points = self.calculate_rotated_points()
        pg.draw.polygon(display,ship_clr,self.points)
        if debug:
            text = font.render(str(round(self.x))+", "+str(round(self.y)),True,(255,255,255))
            display.blit(text,(self.x+ship_scale,self.y+ship_scale))
        


    def move_self(self):
        if self.cooldown[0] > 0:
            self.cooldown[0] -= 1
        if self.laser_cooldown[0] > 0:
            self.laser_cooldown[0] -= 1


        angle2 = self.angle - math.pi/2
        cos_angle = math.cos(angle2)
        sin_angle = math.sin(angle2)


        self.xvel += self.accelleration * cos_angle
        self.yvel += self.accelleration * sin_angle



        # Calculate the current speed of the ship
        current_speed = math.sqrt(self.xvel ** 2 + self.yvel ** 2)

        # Check if the current speed exceeds the ship_speed cap
        if current_speed > ship_speed:
            # If it does, normalize the velocity vector and scale it down to ship_speed
            scaling_factor = ship_speed / current_speed
            self.xvel *= scaling_factor
            self.yvel *= scaling_factor


        self.x,self.y = self.x + self.xvel, self.y + self.yvel



       

        if self.x < -ship_scale:
            self.x = displaysize[0]+ship_scale


        if self.x > displaysize[0]+ship_scale:
            self.x = -ship_scale


        if self.y < -ship_scale:
            self.y = displaysize[1]+ship_scale


        if self.y > displaysize[1]+ship_scale:
            self.y = -ship_scale

    def detect_upgrade_collision(self,upgrade):
        distance = math.sqrt((self.x-upgrade.pos[0])**2+(self.y-upgrade.pos[1])**2)
        if distance < upgrade.radius+ship_scale/2:
            return True
        return False




        

    def attempt_shoot(self):
        global bullets
        if self.sel_weapon == 0 and self.cooldown[0] <= 0:

            bullets.append(bullet_class([self.x,self.y],self.angle-math.pi/2))
            self.cooldown[0] = self.cooldown[1]
        elif self.sel_weapon == 1 and self.laser_cooldown[0] <= 0:
            bullets.append(laser_class((self.x,self.y),self.angle-math.pi/2))
            self.laser_cooldown[0] = self.laser_cooldown[1]


class bullet_class:
    def __init__(self,pos,angle):
        self.points = [list(pos),[pos[0]+math.cos(angle)*bullet_length,pos[1]+math.sin(angle)*bullet_length]]
        self.xvel = bullet_speed * math.cos(angle)
        self.yvel = bullet_speed * math.sin(angle)

    def draw_self(self):
        pg.draw.line(display,bullet_clr,self.points[0],self.points[1],bullet_thickness)
        if debug:
            for asteroid in asteroids:
                pg.draw.line(display,(255,255,255),self.points[1],(asteroid.x,asteroid.y),1)

    def move_self(self):
        global bullets
        for point in self.points:
            point[0] += self.xvel
            point[1] += self.yvel
                
        try:
            if self.points[0][0] > displaysize[0]+bullet_length or self.points[0][0] < -bullet_length:
                bullets.pop(bullets.index(self))
            if self.points[0][1] > displaysize[1]+bullet_length or self.points[0][1] < -bullet_length:
                bullets.pop(bullets.index(self))
        except:
            None

class laser_class:
    def __init__(self,pos,angle):    
        self.start = pos
        self.end = (self.start[0] + 2*displaysize[0] * math.cos(angle),self.start[1] + 2*displaysize[1] * math.sin(angle))
        self.width = ship_scale

    def draw_self(self):
        pg.draw.circle(display,laser_clr,self.start,round(self.width))
        pg.draw.line(display,laser_clr,self.start,self.end,round(self.width))

    def move_self(self):
        global bullets
        if self.width <= 0:
            bullets.pop(bullets.index(self))
        else:
            self.width -= ship_scale*laser_reduction


        
class shootspeed_upgrade_class:
    def __init__(self,pos):
        self.endtime = shootspeed_duration
        self.livetime = 0
        self.pickedup = False
        self.pos = pos
        self.radius = upgrade_radius
        self.color = shootspeed_clr

    def draw_self(self):
        if not self.pickedup:
            pg.draw.circle(display,self.color,self.pos,self.radius)

    def activate_self(self):
        global ship
        self.pickedup = True
        ship.cooldown[1]/=4


            
    def process_self(self):
        global upgrades,ship
        if self.livetime < self.endtime:
            self.livetime += 1
        else:
            upgrades.pop(upgrades.index(self))
            ship.cooldown[1]*=4
            return
        
    





def draw_overlay():
    if ship.sel_weapon == 0:
        var = ship.cooldown[1]-ship.cooldown[0]
        m = ship.cooldown[1]
    elif ship.sel_weapon == 1:
        var = ship.laser_cooldown[1]-ship.laser_cooldown[0]
        m = ship.laser_cooldown[1]


    maxwidth = 300
    height = 25

    x,y = (displaysize[0] - maxwidth/m*var) / 2,displaysize[1]-10-height

    if var != m:
        pg.draw.rect(display,bar1_clr,(x,y,maxwidth/m*var,height))
    else:
        pg.draw.rect(display,bar2_clr,(x,y,maxwidth/m*var,height))


def process_aimbot():
    global ship, asteroids, upgrades

    # Initialize variables to keep track of the closest target and its distance
    closest_target = None
    min_distance = float('inf')

    # Calculate the ship's position
    ship_x, ship_y = ship.x, ship.y

    # Check for upgrades
    if upgrades:
        # Iterate through upgrades to find the closest one
        for upgrade in upgrades:
            upgrade_x, upgrade_y = upgrade.pos

            # Calculate the distance between the ship and the current upgrade
            distance = math.sqrt((upgrade_x - ship_x) ** 2 + (upgrade_y - ship_y) ** 2)

            # If this upgrade is closer than the previous closest, update the closest_target and min_distance
            if distance < min_distance:
                min_distance = distance
                closest_target = upgrade

    # If no upgrades are found or they are further away, consider asteroids
    if not closest_target:
        # Iterate through asteroids to find the closest one
        for asteroid in asteroids:
            asteroid_x, asteroid_y = asteroid.x, asteroid.y

            # Calculate the distance between the ship and the current asteroid
            distance = math.sqrt((asteroid_x - ship_x) ** 2 + (asteroid_y - ship_y) ** 2)

            # If this asteroid is closer than the previous closest, update the closest_target and min_distance
            if distance < min_distance:
                min_distance = distance
                closest_target = asteroid

    # If there is a closest target (either an upgrade or asteroid), calculate the angle towards it
    if closest_target:
        if isinstance(closest_target, shootspeed_upgrade_class):
            target_x, target_y = closest_target.pos
            ship.accelleration = ship_accelleration
        else:
            target_x, target_y = closest_target.x, closest_target.y

        target_angle = math.atan2(target_y - ship_y, target_x - ship_x)

        # Adjust the ship's angle to point towards the closest target
        return target_angle + math.pi / 2

    # If no targets are found (unlikely), return the ship's current angle
    return ship.angle


def spawn_upgrades(pos):
    global upgrades
    if random.random() <= upgrade_chance:
        upgrades.append(random.choice([
            shootspeed_upgrade_class(pos)

            ]))




    

def logic_calls():
    global keystate,ship,asteroids
    for asteroid in asteroids:
        asteroid.move_self()
        asteroid.collide_self()
        asteroid.rotate_self(asteroid_rotation_angle)

    keystate = pg.key.get_pressed()

    if keystate[pg.K_LEFT] or keystate[pg.K_a]:
        ship.angle -= ship_rot_speed
    if keystate[pg.K_RIGHT] or keystate[pg.K_d]:
        ship.angle += ship_rot_speed
        
    ship.accelleration = 0


    if aimbot:
#        ship.angle = process_aimbot()
        targetangle = process_aimbot()
        if ship.angle < targetangle:
            ship.angle += ship_rot_speed
        if ship.angle > targetangle:
            ship.angle -= ship_rot_speed




    if keystate[pg.K_UP] or keystate[pg.K_w]:
        ship.accelleration = ship_accelleration
    if enable_reverse:
        if keystate[pg.K_DOWN] or keystate[pg.K_s]:
            ship.accelleration = -ship_accelleration/2
    if keystate[pg.K_SPACE] or aimbot:
        ship.attempt_shoot()
    

    for bullet in bullets:
        bullet.move_self()

    for upgrade in upgrades:
        if upgrade.pickedup:
            upgrade.process_self()
        else:
            if ship.detect_upgrade_collision(upgrade):
                upgrade.activate_self()




            

    ship.move_self()
        
    clock.tick(clockspeed)


    


def graphic_calls():
    display.fill(background_clr)
    for asteroid in asteroids:
        asteroid.draw_self()

    for bullet in bullets:
        bullet.draw_self()
    for upgrade in upgrades:
        upgrade.draw_self()


    ship.draw_self()
    draw_overlay()

    pg.display.flip()

pg.init()
display = pg.display.set_mode(displaysize)
clock = pg.time.Clock()
font = pg.font.SysFont("Calibri",round(displaysize[0]/40))


def main():
    global asteroids,dead,debug,ship,bullets,aimbot,upgrades
    debug = False
    asteroids = []
    bullets = []
    upgrades = []
    ship = ship_class()
    for i in range(max_asteroids):
        asteroids.append(asteroid_class([0,random.randint(0,displaysize[1])],asteroid_radius,asteroid_points,asteroid_deviation,asteroid_tiers))




    dead = False    
    while not dead:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                dead = True
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    dead = True
                if event.key == pg.K_g:
                    debug = not debug
                if event.key == pg.K_SPACE:
                    ship.attempt_shoot()
                if event.key == pg.K_b:
                    aimbot= not aimbot

                if event.key == pg.K_1:
                    ship.sel_weapon = 0
                    print("selected Peashooter")
                if event.key == pg.K_2:
                    ship.sel_weapon = 1
                    print("selected laser")     
                

                


        logic_calls()
        graphic_calls()

    


main()
pg.quit()
quit()















