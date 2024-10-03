class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 1

    def Move(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        #Check if the bullet is out of bounds
        if self.x < 0 or self.x > 1600 or self.y < 0 or self.y > 1600:
            return True

    def Explode(self):   
        return (self.x, self.y)