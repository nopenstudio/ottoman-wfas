"""Source regressions; run with Python 2.7. These are not engine smoke tests."""
import copy
import os
import subprocess
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from header_common import *
from header_items import *
from header_troops import *
from header_skills import *
from header_operations import *
from header_animations import *
from header_triggers import *
from module_constants import *
from module_items import items
from module_troops import troops
from module_animations import animations
from module_scripts import scripts
from module_mission_templates import mission_templates
from module_canakkale import canakkale_scripts, canakkale_mission_triggers

BASE = '27989be0cad49d55055e44af8bbc293f5ece95d1'
I = dict((x[0], x) for x in items)
T = dict((x[0], x) for x in troops)
S = dict(scripts)
# Two rifles, four visual mappings, six unambiguous default slots per side.
SIDES = [
 ('khergit_veteran_footman_multiplayer','khergit_dismounted_lancer_multiplayer_ai',
  fac_kingdom_3,'canakkale_turk_rifle','canakkale_turk_cap','yanichar_forma_b',
  'janichar2','turk-cap','janissary_tapki','m_yatagan_bad'),
 ('nord_scout_multiplayer','nord_scout_multiplayer_ai',fac_kingdom_4,
  'canakkale_british_rifle','canakkale_british_helmet','yanichar_forma_a',
  'janichar1','ingiliz-cap','cavalry_boots','bad_palash')]

def baseline(filename, variable):
    source = subprocess.check_output(['git','show',BASE+':'+filename])
    namespace = {'__name__':'baseline_'+variable}
    exec(compile(source, filename, 'exec'), namespace)
    return namespace[variable]

class SourceTests(unittest.TestCase):
    def test_existing_item_ids_and_definitions_preserved(self):
        old=baseline('module_items.py','items')
        self.assertEqual(items[:len(old)-1],old[:-1])
        self.assertEqual(items[-1],old[-1])
        self.assertEqual(len(items),len(old)+4)
    def test_two_seven_round_clones(self):
        for new,base in [('canakkale_turk_rifle','t_norm_musket'),
                         ('canakkale_british_rifle','norm_musket')]:
            rifle,stock=I[new],I[base]
            self.assertEqual(rifle[2],stock[2])
            self.assertEqual(rifle[4:6],stock[4:6])
            self.assertEqual(get_max_ammo(rifle[6]),7)
            self.assertEqual(get_max_ammo(stock[6]),1)
            self.assertEqual(rifle[3]&0xff,itp_type_crossbow)
            self.assertFalse(rifle[3]&itp_next_item_as_melee)
            self.assertEqual(rifle[8][0][0],ti_on_weapon_attack)
            self.assertIn((call_script,'script_canakkale_rifle_fired',':shooter'),rifle[8][0][1])
    def test_visuals_inventory_stats_and_foot_spawn(self):
        ids=dict((x[0],i) for i,x in enumerate(items))
        for player,bot,fac,rifle,cap,uniform,bodymesh,headmesh,boots,backup in SIDES:
            self.assertEqual(I[uniform][2][0][0],bodymesh)
            self.assertEqual(I[cap][2],[(headmesh,0)])
            self.assertEqual(I[cap][3]&0xff,itp_type_head_armor)
            expected=set(ids[x] for x in [rifle,cap,uniform,boots,backup,'norm_bullets'])
            for name in [player,bot]:
                t=T[name]
                self.assertEqual(t[6],fac)
                self.assertEqual(set(t[7]),expected)
                self.assertFalse(t[3]&(tf_mounted|tf_guarantee_horse))
                self.assertEqual((t[10]>>(4*skl_riding))&15,0)
                self.assertEqual((t[10]>>(4*skl_horse_archery))&15,0)
                self.assertGreaterEqual(t[8]&0xff,get_difficulty(I[rifle][6]))
                counts={}
                weapons=0
                for itemid in t[7]:
                    typ=items[itemid][3]&0xff
                    self.assertNotEqual(typ,itp_type_horse)
                    self.assertNotIn(typ,[itp_type_bow,itp_type_arrows,itp_type_shield])
                    if typ in [itp_type_head_armor,itp_type_body_armor,itp_type_foot_armor]:
                        counts[typ]=counts.get(typ,0)+1
                    else:weapons+=1
                self.assertEqual(sorted(counts.values()),[1,1,1])
                self.assertLessEqual(weapons,4)
    def test_troop_ids_and_captain_preserved(self):
        old=baseline('module_troops.py','troops')
        self.assertEqual([t[0] for t in troops],[t[0] for t in old])
        begin=next(i for i,t in enumerate(troops) if t[0]=='mp_swadian_militia')
        self.assertEqual(troops[begin:],old[begin:])
        # Normal bot spawn/selection uses exactly these faction-filtered ranges.
        ids=dict((t[0],i) for i,t in enumerate(troops))
        ranges=[(ids['swadian_crossbowman_multiplayer_ai'],ids['swadian_crossbowman_multiplayer'],1),
                (ids['swadian_crossbowman_multiplayer'],ids['multiplayer_end'],0)]
        for begin,end,botindex in ranges:
            for side in SIDES:
                names=[t[0] for t in troops[begin:end] if t[6]==side[2]]
                self.assertEqual(names,[side[botindex]])
    def test_availability_matches_defaults_and_classification(self):
        init=S['game_quick_start'];idname=dict((i,x[0]) for i,x in enumerate(items))
        itemclasses=dict((o[1],o[3]) for o in init if isinstance(o,tuple) and o[0]==item_set_slot and o[2]==slot_item_multiplayer_item_class)
        classification=S['multiplayer_get_troop_class']
        for side in SIDES:
            player=side[0]
            allowed=set(o[2] for o in init if isinstance(o,tuple) and o[0]==call_script and
                        o[1]=='script_multiplayer_set_item_available_for_troop' and o[3]=='trp_'+player)
            expected=set('itm_'+idname[i] for i in T[player][7])
            self.assertEqual(allowed,expected)
            self.assertTrue(all(x in itemclasses for x in expected))
            self.assertEqual(itemclasses['itm_'+side[3]],multi_item_class_type_crossbow)
            self.assertIn((assign,':troop_class',multi_troop_class_crossbowman),classification[:8])
        # The removed cavalry record cannot match that old branch anymore.
        oldcav=[o for o in classification[10:] if isinstance(o,tuple) and len(o)>2 and o[1]==':troop_no' and o[2]=='trp_nord_scout_multiplayer']
        self.assertEqual(oldcav,[])
    def test_animation_resource_range_and_lock_flags(self):
        old=baseline('module_animations.py','animations')
        self.assertEqual(animations[:-1],old)
        a=animations[-1]
        self.assertEqual(a[0],'rifle_bolt_cycle_2s')
        self.assertEqual(a[3][:4],[2.0,'rifle_bolt_cycle_2s',0,60])
        self.assertEqual(a[2]&amf_priority_mask,90)
        self.assertFalse(a[2]&amf_use_weapon_speed)
        self.assertFalse(a[1]&acf_rot_vertical_mask)
        self.assertTrue(a[3][4]&arf_stick_item_to_left_hand)
    def test_only_normal_missions_get_lifecycle_guards(self):
        old=baseline('module_mission_templates.py','mission_templates')
        wanted=set(['multiplayer_dm','multiplayer_tdm','multiplayer_cf','multiplayer_sg','multiplayer_bt','multiplayer_duel'])
        for before,after in zip(old,mission_templates):
            if after[0] in wanted:
                self.assertEqual(after[5][:-2],before[5])
                self.assertEqual(after[5][-2:],canakkale_mission_triggers)
            else:self.assertEqual(after,before)
    def test_no_ammo_rewrite_or_untrusted_client_command(self):
        forbidden=set([agent_set_ammo,agent_refill_ammo,agent_equip_item,agent_unequip_item])
        for name,ops in canakkale_scripts:
            self.assertFalse(any(isinstance(o,tuple) and o[0] in forbidden for o in ops))
        handler=S['game_receive_network_message']
        i=handler.index((eq,':event_type',multiplayer_event_canakkale_bolt))
        self.assertIn(neg|multiplayer_is_server,handler[i:i+6])
        self.assertIn((eq,':player_no',0),handler[i:i+6])
        self.assertNotIn('anim_ready_musket',repr(canakkale_scripts))

if __name__=='__main__':unittest.main(verbosity=2)
