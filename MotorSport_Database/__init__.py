from .MotorSport_Database import MOTORSPORT_DATABASE

def setup(bot):
    bot.add_cog(MOTORSPORT_DATABASE(bot))
