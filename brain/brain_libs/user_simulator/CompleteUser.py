from User import *
import UserSimulation

class CompleteUser(object):
        MAX_TURN = 100
        user_intent = None
        user_slot = None
        generate = UserSimulation.intent_slot_generator()
        user_intent = generate.goal["intent"]
        user_slot = generate.goal["slot"]
        sim_user = User(intent = user_intent, slot = user_slot)
        #  sim_user=User(None,None)
        turn = 0

        @staticmethod
        def initial(intent = 0):
                CompleteUser.generate = UserSimulation.intent_slot_generator()
                CompleteUser.user_intent = CompleteUser.generate.goal["intent"] if intent == 0 else intent
                print(CompleteUser.user_intent)
                CompleteUser.user_slot = CompleteUser.generate.goal["slot"]
                print(CompleteUser.user_slot)
                CompleteUser.sim_user = User(intent = CompleteUser.user_intent, slot = CompleteUser.user_slot)
                CompleteUser.turn = 0
        @staticmethod
        def step(DM):
            end = False
            Success = False
            if CompleteUser.turn == 0:
                user_word, reward_once, end, Success = CompleteUser.sim_user.respond(None)
                CompleteUser.turn += 1
            elif CompleteUser.turn > CompleteUser.MAX_TURN:
                #  CompleteUser.initial()
                print(True)
                return '浪費我時間', -100, True, False
            else:
                user_word , reward_once, end, Success = CompleteUser.sim_user.respond(DM)
                CompleteUser.turn += 1
            #  if end == True:
            #      user_word, reward_once, end = ComplereUser.sim_user.respond(DM)
            #      CompleteUser.initial()
            return user_word , reward_once, end, Success

def main():
    sim_user = CompleteUser()
    for i in range(1,6):
        print("--- initializing user simulator ---")
        CompleteUser.initial(intent = i)
if __name__ == "__main__":
    main()
