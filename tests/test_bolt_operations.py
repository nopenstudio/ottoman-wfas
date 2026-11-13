"""Execute the actual operation tuples against an in-memory host/client harness.

This verifies script state/control flow, not the WFaS engine's input/projectiles.
"""
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from header_common import *
from header_operations import *
from module_constants import *
from module_canakkale import canakkale_scripts
from module_scripts import scripts

S = dict(scripts)
def op(x):return x if isinstance(x,tuple) else (x,)

def parse(ops, start=0, nested=False):
    nodes=[];i=start
    while i<len(ops):
        item=op(ops[i]);code=item[0]
        if code in [else_try,try_end]:return nodes,i
        if code in [try_begin,try_for_agents,try_for_range]:
            body,j=parse(ops,i+1,True);branches=[body]
            while j<len(ops) and op(ops[j])[0]==else_try:
                body,j=parse(ops,j+1,True);branches.append(body)
            assert j<len(ops) and op(ops[j])[0]==try_end
            nodes.append(('block',item,branches));i=j+1
        else:nodes.append(('op',item));i+=1
    assert not nested
    return nodes,i

class VM(object):
    def __init__(self,server=True,local=7):
        self.now=1000;self.server=server;self.local=local;self.alive=True
        self.slots={};self.animation='anim_stand_crossbow';self.events=[];self.animations=[]
        self.globals={'$g_multiplayer_is_game_type_captain':0}
        self.registers={}
        self.weapon="itm_canakkale_turk_rifle"
    def run(self,name,params=()):
        return self.execute(parse(S[name])[0],{},params)
    def value(self,x,v):return v.get(x,self.globals.get(x,x)) if isinstance(x,str) else x
    def execute(self,nodes,v,params):
        or_pending=False;or_value=False
        for node in nodes:
            if node[0]=='block':
                item,branches=node[1:];code=item[0]
                if code==try_begin:
                    for branch in branches:
                        if self.execute(branch,v,params):break
                else:
                    values=[7] if code==try_for_agents else range(self.value(item[2],v),self.value(item[3],v))
                    for n in values:v[item[1]]=n;self.execute(branches[0],v,params)
                continue
            item=node[1];code=item[0];negative=bool(code&neg);or_flag=bool(code&this_or_next);code&=~(neg|this_or_next)
            a=item[1:];get=lambda x:self.value(x,v);ok=True
            if code==store_script_param_1:v[a[0]]=params[0]
            elif code==store_script_param:v[a[0]]=params[a[1]-1]
            elif code in [agent_is_active,agent_is_human]:ok=get(a[0])==7
            elif code==agent_is_alive:ok=self.alive and get(a[0])==7
            elif code==multiplayer_is_server:ok=self.server
            elif code==multiplayer_is_dedicated_server:ok=False
            elif code==assign:
                if isinstance(a[0],int):self.registers[a[0]]=get(a[1])
                else:v[a[0]]=get(a[1])
            elif code==eq:ok=get(a[0])==get(a[1])
            elif code==neq:ok=get(a[0])!=get(a[1])
            elif code==lt:ok=get(a[0])<get(a[1])
            elif code==le:ok=get(a[0])<=get(a[1])
            elif code==gt:ok=get(a[0])>get(a[1])
            elif code==ge:ok=get(a[0])>=get(a[1])
            elif code==store_mission_timer_a_msec:v[a[0]]=self.now
            elif code==agent_get_slot:v[a[0]]=self.slots.get((get(a[1]),get(a[2])),0)
            elif code==agent_set_slot:self.slots[(get(a[0]),get(a[1]))]=get(a[2])
            elif code==store_add:v[a[0]]=get(a[1])+get(a[2])
            elif code==val_add:v[a[0]]=get(a[0])+get(a[1])
            elif code==val_sub:v[a[0]]=get(a[0])-get(a[1])
            elif code==get_max_players:v[a[0]]=3
            elif code==player_is_active:ok=get(a[0]) in [1,2]
            elif code==get_player_agent_no:v[a[0]]=self.local
            elif code in [multiplayer_send_int_to_player,multiplayer_send_2_int_to_player]:self.events.append(tuple(get(x) for x in a))
            elif code==agent_get_wielded_item:v[a[0]]=self.weapon
            elif code==store_trigger_param_1:v[a[0]]=7
            elif code==agent_get_animation:v[a[0]]=self.animation
            elif code==agent_set_animation:self.animation=a[1];self.animations.append((self.now,)+a)
            elif code==call_script:self.run(a[0][7:],tuple(get(x) for x in a[1:]))
            else:raise AssertionError('Unimplemented executed opcode: %r'% (item,))
            if negative:ok=not ok
            if or_flag:
                or_pending=True;or_value=or_value or ok
                continue
            if or_pending:
                ok=or_value or ok;or_pending=False;or_value=False
            if not ok:return False
        return True
    def until(self):return self.slots.get((7,slot_agent_canakkale_bolt_until),0)

class BoltStateTests(unittest.TestCase):
    def moving(self,m):
        return [x for x in m.animations if x[2]=='anim_rifle_bolt_cycle_2s']
    def holds(self,m):
        return [x for x in m.animations if x[2]=='anim_canakkale_bolt_hold']
    def receive(self,m,stamp=1001,sender=0):
        m.run('game_receive_network_message',[sender,multiplayer_event_canakkale_bolt,7,stamp])
    def test_one_shot_one_animation_across_two_seconds_of_ticks(self):
        m=VM();m.run('canakkale_rifle_fired',[7])
        self.assertEqual(m.until(),3000)
        self.assertEqual(m.events,[(1,multiplayer_event_canakkale_bolt,7,1001),
                                   (2,multiplayer_event_canakkale_bolt,7,1001)])
        for now in range(1000,3000,10):m.now=now;m.run('canakkale_bolt_tick')
        self.assertEqual(len(self.moving(m)),1);self.assertEqual(len(m.animations),1)
        m.now=3000;m.run('canakkale_bolt_tick')
        self.assertEqual(m.until(),0);self.assertEqual(m.animation,'anim_stand')
    def test_four_rapid_server_attacks_do_not_replay_extend_or_rebroadcast(self):
        m=VM();m.run('canakkale_rifle_fired',[7])
        for now in [1100,1200,1300,1400]:
            m.now=now;m.run('canakkale_rifle_fired',[7]);m.run('canakkale_bolt_tick')
        self.assertEqual(m.until(),3000);self.assertEqual(len(self.moving(m)),1)
        self.assertEqual(len(m.animations),1);self.assertEqual(len(m.events),2)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_early_shots)],4)
    def test_four_owner_attacks_and_echoes_do_not_restart_prediction(self):
        m=VM(False);m.run('canakkale_rifle_fired',[7])
        for now in [1100,1200,1300,1400]:
            m.now=now;m.run('canakkale_rifle_fired',[7]);self.receive(m)
        self.assertEqual(m.until(),3000);self.assertEqual(len(m.animations),1)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_predictions)],0)
    def test_four_observer_duplicate_events_do_not_replay(self):
        m=VM(False,8);self.receive(m)
        for now in [1100,1200,1300,1400]:m.now=now;self.receive(m)
        self.assertEqual(m.until(),3000);self.assertEqual(len(m.animations),1)
    def test_swap_cancels_once_and_leaves_unrelated_weapon_alone(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=1500;m.weapon='itm_bad_palash'
        m.run('canakkale_bolt_tick')
        self.assertEqual(m.animation,'anim_stand');self.assertEqual(m.until(),3000)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_visual)],0)
        m.animation='anim_ready_sword'
        for now in [1510,1600,1800,2999]:m.now=now;m.run('canakkale_bolt_tick')
        self.assertEqual(m.animation,'anim_ready_sword');self.assertEqual(len(m.animations),2)
        m.now=3000;m.run('canakkale_bolt_tick')
        self.assertEqual(m.animation,'anim_ready_sword');self.assertEqual(m.until(),0)
    def test_swap_back_holds_remaining_deadline_without_moving_replay(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=1500;m.weapon='itm_bad_palash';m.run('canakkale_bolt_tick')
        m.now=1600;m.weapon='itm_canakkale_turk_rifle';m.run('canakkale_bolt_tick')
        self.assertEqual(m.animation,'anim_canakkale_bolt_hold');self.assertEqual(m.until(),3000)
        for now in [1700,1800,1900,2999]:m.now=now;m.run('canakkale_rifle_fired',[7]);m.run('canakkale_bolt_tick')
        self.assertEqual(len(self.moving(m)),1);self.assertEqual(len(self.holds(m)),1)
        self.assertEqual(m.until(),3000)
        m.now=3000;m.run('canakkale_bolt_tick');self.assertEqual(m.until(),0)
    def test_switching_between_two_rifles_never_replays_bolt(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=1400;m.weapon='itm_canakkale_british_rifle'
        m.run('canakkale_bolt_tick')
        self.assertEqual(len(self.moving(m)),1);self.assertEqual(len(self.holds(m)),1)
        self.assertEqual(m.until(),3000)
    def test_empty_hand_swap_uses_no_firearm_animation(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=1500;m.weapon=-1;m.run('canakkale_bolt_tick')
        self.assertEqual(m.animation,'anim_stand');self.assertEqual(len(self.holds(m)),0)
        self.assertEqual(m.until(),3000)
    def test_interrupted_animation_is_not_restarted_by_get_animation_mismatch(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.animation='anim_ready_musket'
        for now in range(1100,3000,10):m.now=now;m.run('canakkale_bolt_tick')
        self.assertEqual(len(m.animations),1);self.assertEqual(m.until(),3000)
        m.now=3000;m.run('canakkale_bolt_tick');self.assertEqual(m.animation,'anim_stand')
    def test_late_owner_echo_after_expiry_does_not_start_second_cycle(self):
        m=VM(False);m.run('canakkale_rifle_fired',[7]);m.now=3000;m.run('canakkale_bolt_tick')
        m.now=3500;self.receive(m)
        self.assertEqual(m.until(),0);self.assertEqual(len(self.moving(m)),1)
    def test_late_observer_duplicates_and_old_events_are_rejected(self):
        m=VM(False,8);self.receive(m);m.now=3000;m.run('canakkale_bolt_tick')
        m.now=3500;self.receive(m);self.receive(m,900)
        self.assertEqual(m.until(),0);self.assertEqual(len(self.moving(m)),1)
        m.now=4000;self.receive(m,4001)
        self.assertEqual(m.until(),6000);self.assertEqual(len(self.moving(m)),2)
    def test_owner_without_prediction_can_receive_legitimate_server_action(self):
        m=VM(False);self.receive(m)
        self.assertEqual(m.until(),3000);self.assertEqual(len(self.moving(m)),1)
    def test_delayed_acknowledgements_for_two_predictions_do_not_replay(self):
        m=VM(False);m.run('canakkale_rifle_fired',[7]);m.now=3000;m.run('canakkale_bolt_tick')
        m.now=4000;m.run('canakkale_rifle_fired',[7]);m.now=6000;m.run('canakkale_bolt_tick')
        m.now=6500;self.receive(m,1001);self.receive(m,4001);self.receive(m,4001)
        self.assertEqual(m.until(),0);self.assertEqual(len(self.moving(m)),2)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_predictions)],0)
    def test_event_arriving_after_weapon_swap_does_not_animate_sword(self):
        m=VM(False,8);m.weapon='itm_bad_palash';self.receive(m)
        self.assertEqual(m.until(),3000);self.assertEqual(m.animations,[])
        m.now=1600;m.weapon='itm_canakkale_turk_rifle';m.run('canakkale_bolt_tick')
        self.assertEqual(len(self.moving(m)),0);self.assertEqual(len(self.holds(m)),1)
    def test_expiry_clears_state_once_regardless_of_reported_animation(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.animation='anim_some_transient_action'
        m.now=3000;m.run('canakkale_bolt_tick');self.assertEqual(m.animation,'anim_stand')
        calls=len(m.animations)
        for now in [3010,3100,3500]:m.now=now;m.run('canakkale_bolt_tick')
        self.assertEqual(len(m.animations),calls)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_weapon)],-1)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_visual)],0)
    def test_forged_event_is_ignored_by_server_and_other_clients(self):
        for m in [VM(True),VM(False)]:self.receive(m,sender=1);self.assertEqual(m.until(),0)
    def test_actual_troop_classifier_uses_rifle_not_cavalry_classes(self):
        for troop in ['trp_khergit_veteran_footman_multiplayer','trp_nord_scout_multiplayer']:
            m=VM();m.run('multiplayer_get_troop_class',[troop]);self.assertEqual(m.registers[reg0],multi_troop_class_crossbowman)
        m=VM();m.run('multiplayer_get_troop_class',['trp_swadian_man_at_arms_multiplayer']);self.assertEqual(m.registers[reg0],multi_troop_class_cavalry)
    def test_death_and_captain_do_not_start_or_reassert(self):
        m=VM();m.alive=False;m.run('canakkale_rifle_fired',[7]);self.assertEqual(m.until(),0)
        m=VM();m.globals['$g_multiplayer_is_game_type_captain']=1
        m.run('canakkale_rifle_fired',[7]);self.assertEqual(m.until(),0)
    def test_spawn_resets_visual_weapon_prediction_and_dedupe_state(self):
        from module_canakkale import canakkale_mission_triggers
        m=VM(False);m.run('canakkale_rifle_fired',[7]);self.receive(m)
        m.execute(parse(canakkale_mission_triggers[0][4])[0],{},())
        for slot in [slot_agent_canakkale_bolt_until,slot_agent_canakkale_early_shots,
                     slot_agent_canakkale_bolt_visual,slot_agent_canakkale_bolt_last_event,
                     slot_agent_canakkale_bolt_predictions]:self.assertEqual(m.slots[(7,slot)],0)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_bolt_weapon)],-1)

if __name__=='__main__':unittest.main(verbosity=2)
