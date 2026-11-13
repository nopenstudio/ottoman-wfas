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
            elif code==get_max_players:v[a[0]]=3
            elif code==player_is_active:ok=get(a[0]) in [1,2]
            elif code==get_player_agent_no:v[a[0]]=self.local
            elif code==multiplayer_send_int_to_player:self.events.append(tuple(get(x) for x in a))
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
    def test_server_starts_two_second_cycle_and_broadcasts(self):
        m=VM();m.run('canakkale_rifle_fired',[7])
        self.assertEqual(m.until(),3000)
        self.assertEqual(m.animation,'anim_rifle_bolt_cycle_2s')
        self.assertEqual(m.events,[(1,multiplayer_event_canakkale_bolt,7),(2,multiplayer_event_canakkale_bolt,7)])
    def test_prediction_duplicate_does_not_extend_or_restart(self):
        m=VM(False);m.run('canakkale_rifle_fired',[7]);m.now=1250
        m.run('game_receive_network_message',[0,multiplayer_event_canakkale_bolt,7])
        self.assertEqual(m.until(),3000);self.assertEqual(len(m.animations),1)
    def test_interrupted_ready_reasserted_then_released_at_deadline(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=2999;m.animation='anim_ready_musket'
        m.run('canakkale_bolt_tick');self.assertEqual(m.animation,'anim_rifle_bolt_cycle_2s')
        m.now=3000;m.run('canakkale_bolt_tick')
        self.assertEqual(m.until(),0);self.assertEqual(m.animation,'anim_stand_crossbow')
    def test_early_attack_is_detected_not_falsely_cancelled(self):
        m=VM();m.run('canakkale_rifle_fired',[7]);m.now=1100;m.run('canakkale_rifle_fired',[7])
        self.assertEqual(m.until(),3000)
        self.assertEqual(m.slots[(7,slot_agent_canakkale_early_shots)],1)
        self.assertEqual(len(m.events),2)
    def test_non_owner_client_does_not_predict_other_agents(self):
        m=VM(False,8);m.run('canakkale_rifle_fired',[7]);self.assertEqual(m.until(),0)
        m.run('game_receive_network_message',[0,multiplayer_event_canakkale_bolt,7])
        self.assertEqual(m.until(),3000)
    def test_forged_event_is_ignored_by_server_and_other_clients(self):
        for m in [VM(True),VM(False)]:
            m.run('game_receive_network_message',[1,multiplayer_event_canakkale_bolt,7])
            self.assertEqual(m.until(),0)
    def test_actual_troop_classifier_uses_rifle_not_cavalry_classes(self):
        for troop in ['trp_khergit_veteran_footman_multiplayer','trp_nord_scout_multiplayer']:
            m=VM();m.run('multiplayer_get_troop_class',[troop])
            self.assertEqual(m.registers[reg0],multi_troop_class_crossbowman)
        m=VM();m.run('multiplayer_get_troop_class',['trp_swadian_man_at_arms_multiplayer'])
        self.assertEqual(m.registers[reg0],multi_troop_class_cavalry)
    def test_death_and_captain_do_not_start_or_reassert(self):
        m=VM();m.alive=False;m.run('canakkale_rifle_fired',[7]);self.assertEqual(m.until(),0)
        m=VM();m.globals['$g_multiplayer_is_game_type_captain']=1
        m.run('canakkale_rifle_fired',[7]);self.assertEqual(m.until(),0)

if __name__=='__main__':unittest.main(verbosity=2)
