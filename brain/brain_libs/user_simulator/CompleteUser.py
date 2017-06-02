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
	turn = 0
	def initial():
		user_intent = generate.goal["intent"]
		user_slot = generate.goal["slot"]
		CompleteUser.sim_user = User(intent = user_intent, slot = user_slot)
		CompleteUser.turn = 0
	def respond(DM):
		if turn == 0:
	    	user_word, reward_once, end = sim_user.respond(None)
	    	turn++
	    elif turn > MAX_TURN:
	    	initial()
	    	return '浪費我時間', User.reward_fail,True 
	    else:
	    	user_word , reward_once, end = CompleteUser.sim_user.respond(DM)
	    	turn++
	    if end == True
	    	initial()
	    return user_word , reward_once, end