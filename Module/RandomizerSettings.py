import random
from itertools import chain

from Class import settingkey
from Class.exceptions import SettingsException
from Class.seedSettings import SeedSettings, makeKHBRSettings
from List import experienceValues
from List.configDict import (
    locationType,
    itemType,
    locationDepth,
    StartingMovementOption,
    SoraLevelOption,
    itemDifficulty,
    ItemAccessibilityOption,
    itemRarity,
    SoftlockPreventionOption,
    AbilityPoolOption,
    expCurve,
)
from List.hashTextEntries import generate_hash_icons
from List.inventory import storyunlock, report, proof, form
from Module.modifier import SeedModifier
from Module.progressionPoints import ProgressionPoints


class RandomizerSettings:
    excludeFrom50 = list(
        chain(
            [
                1,
                3,
                5,
                6,
                8,
                11,
                13,
                16,
                18,
                19,
                21,
                22,
                24,
                26,
                27,
                29,
                31,
                33,
                35,
                37,
                38,
                40,
                42,
                43,
                45,
                47,
                49,
            ],
            range(51, 100),
        )
    )
    excludeFrom99 = [
        1,
        2,
        3,
        4,
        5,
        6,
        8,
        10,
        11,
        13,
        14,
        16,
        18,
        19,
        21,
        22,
        24,
        26,
        27,
        29,
        30,
        32,
        34,
        35,
        37,
        38,
        40,
        42,
        43,
        45,
        46,
        48,
        50,
        51,
        52,
        54,
        55,
        56,
        57,
        58,
        60,
        61,
        62,
        63,
        64,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
    ]

    def __init__(
        self,
        seed_name: str,
        spoiler_log: bool,
        ui_version: str,
        ui_settings: SeedSettings,
        seed_string: str,
    ):
        self.ui_settings = ui_settings
        self.seed_string = seed_string
        self.crit_mode = ui_settings.get(settingkey.CRITICAL_BONUS_REWARDS)
        self.item_accessibility = ItemAccessibilityOption(
            ui_settings.get(settingkey.ACCESSIBILITY)
        )

        include_list = []
        vanilla_list = []
        include_list_keys = [
            (settingkey.CRITICAL_BONUS_REWARDS, "Critical Bonuses"),
            (settingkey.GARDEN_OF_ASSEMBLAGE_REWARDS, "Garden of Assemblage"),
        ]
        for key in include_list_keys:
            if ui_settings.get(key[0]):
                include_list.append(key[1])
        worlds_with_rewards = ui_settings.get(settingkey.WORLDS_WITH_REWARDS)
        vanilla_worlds = []
        if isinstance(worlds_with_rewards[0], list):
            vanilla_worlds = worlds_with_rewards[1]
            worlds_with_rewards = worlds_with_rewards[0]
        for location in worlds_with_rewards:
            include_list.append(locationType[location].value)
        for location in vanilla_worlds:
            vanilla_list.append(locationType[location].value)
        for location in ui_settings.get(settingkey.SUPERBOSSES_WITH_REWARDS):
            include_list.append(locationType[location].value)
        for location in ui_settings.get(settingkey.MISC_LOCATIONS_WITH_REWARDS):
            include_list.append(locationType[location].value)
        self.enabledLocations: list[locationType] = [
            l for l in locationType if l in include_list
        ]
        self.vanillaLocations: list[locationType] = [
            l for l in locationType if l in vanilla_list
        ]
        self.disabledLocations: list[locationType] = [
            l
            for l in locationType
            if l not in include_list
            and l not in [locationType.Mush13, locationType.WeaponSlot]
        ]

        level_setting = SoraLevelOption(ui_settings.get(settingkey.SORA_LEVELS))
        self.vanilla_level_one = False
        if level_setting == SoraLevelOption.LEVEL_1:
            self.max_level_checks = 1
            if locationType.Level in self.enabledLocations:
                raise SettingsException(
                    "Please choose between Junk or Vanilla Checks when doing Level 1"
                )
            elif locationType.Level in self.vanillaLocations:
                self.vanilla_level_one = True
        elif level_setting == SoraLevelOption.LEVEL_50:
            self.max_level_checks = 50
        elif level_setting == SoraLevelOption.LEVEL_99:
            self.max_level_checks = 99
        else:
            raise SettingsException("Invalid Level choice")

        self.split_levels: bool = ui_settings.get(settingkey.SPLIT_LEVELS)
        self.battle_level_rando: str = ui_settings.get(settingkey.BATTLE_LEVEL_RANDO)
        self.battle_level_offset: int = ui_settings.get(settingkey.BATTLE_LEVEL_OFFSET)
        self.battle_level_range: int = ui_settings.get(settingkey.BATTLE_LEVEL_RANGE)

        self.starting_inventory_ids: list[int] = [
            int(value) for value in ui_settings.get(settingkey.STARTING_INVENTORY)
        ]
        self.starting_growth_option = StartingMovementOption(
            ui_settings.get(settingkey.STARTING_MOVEMENT)
        )
        self.starting_report_count: int = ui_settings.get(settingkey.STARTING_REPORTS)
        self.starting_story_unlock_ids = [
            int(value) for value in ui_settings.get(settingkey.STARTING_STORY_UNLOCKS)
        ]

        self.itemDifficulty = itemDifficulty(
            ui_settings.get(settingkey.ITEM_PLACEMENT_DIFFICULTY)
        )
        self.extended_placement_logic: bool = ui_settings.get(
            settingkey.NIGHTMARE_LOGIC
        )
        self.story_unlock_rarity: itemRarity = ui_settings.get(
            settingkey.STORY_UNLOCK_CATEGORY
        )

        softlock_option = SoftlockPreventionOption(
            ui_settings.get(settingkey.SOFTLOCK_CHECKING)
        )
        self.regular_rando: bool = softlock_option in [
            SoftlockPreventionOption.DEFAULT,
            SoftlockPreventionOption.BOTH,
        ]
        self.reverse_rando: bool = softlock_option in [
            SoftlockPreventionOption.REVERSE,
            SoftlockPreventionOption.BOTH,
        ]

        self.level_stat_pool = SeedModifier.level_up_stat_pool_weighted(
            str_rate=ui_settings.get(settingkey.SORA_STR_RATE),
            mag_rate=ui_settings.get(settingkey.SORA_MAG_RATE),
            def_rate=ui_settings.get(settingkey.SORA_DEF_RATE),
            ap_rate=ui_settings.get(settingkey.SORA_AP_RATE),
        )

        self.junk_pool: list[int] = [
            int(item_id) for item_id in ui_settings.get(settingkey.JUNK_ITEMS)
        ]
        if len(self.junk_pool) == 0:
            raise SettingsException("Need at least one junk item in the pool")

        self.sora_ap: int = ui_settings.get(settingkey.SORA_AP)
        self.donald_ap: int = ui_settings.get(settingkey.DONALD_AP)
        self.goofy_ap: int = ui_settings.get(settingkey.GOOFY_AP)
        self.ability_pool_option = AbilityPoolOption(
            ui_settings.get(settingkey.ABILITY_POOL)
        )
        self.promiseCharm: bool = ui_settings.get(settingkey.ENABLE_PROMISE_CHARM)
        self.auto_equip_abilities: bool = ui_settings.get(
            settingkey.AUTO_EQUIP_START_ABILITIES
        )
        self.tt1_jailbreak: bool = True  # ui_settings.get(settingkey.TT1_JAILBREAK)
        self.pureblood: bool = True  # ui_settings.get(settingkey.PUREBLOOD)
        self.antiform: bool = ui_settings.get(settingkey.ANTIFORM)
        self.fifty_ap: bool = ui_settings.get(settingkey.FIFTY_AP_BOOSTS)
        self.hintsType: str = ui_settings.get(settingkey.HINT_SYSTEM)
        self.reportDepth = locationDepth(ui_settings.get(settingkey.REPORT_DEPTH))
        self.proofDepth = locationDepth(ui_settings.get(settingkey.PROOF_DEPTH))
        self.storyDepth = locationDepth(ui_settings.get(settingkey.STORY_UNLOCK_DEPTH))

        if softlock_option == SoftlockPreventionOption.BOTH:
            if self.proofDepth in [
                locationDepth.FirstBoss,
                locationDepth.LastStoryBoss,
                locationDepth.FirstVisit,
            ]:
                raise SettingsException(
                    f"Setting proof depth to {self.proofDepth} will contradict either regular or reverse rando. Please use another setting"
                )
            if self.reportDepth in [
                locationDepth.FirstBoss,
                locationDepth.LastStoryBoss,
                locationDepth.FirstVisit,
            ]:
                raise SettingsException(
                    f"Setting report depth to {self.reportDepth} will contradict either regular or reverse rando. Please use another setting"
                )
            if self.storyDepth in [
                locationDepth.FirstBoss,
                locationDepth.LastStoryBoss,
                locationDepth.FirstVisit,
            ]:
                raise SettingsException(
                    f"Setting visit unlock depth to {self.storyDepth} will contradict either regular or reverse rando. Please use another setting"
                )

        self.prevent_self_hinting: bool = ui_settings.get(
            settingkey.PREVENT_SELF_HINTING
        )
        self.allow_proof_hinting: bool = ui_settings.get(settingkey.ALLOW_PROOF_HINTING)
        self.allow_report_hinting: bool = ui_settings.get(
            settingkey.ALLOW_REPORT_HINTING
        )
        self.keyblade_support_abilities: list[int] = [
            int(ability_id)
            for ability_id in ui_settings.get(settingkey.KEYBLADE_SUPPORT_ABILITIES)
        ]
        self.keyblade_action_abilities: list[int] = [
            int(ability_id)
            for ability_id in ui_settings.get(settingkey.KEYBLADE_ACTION_ABILITIES)
        ]
        self.keyblade_min_stat: int = ui_settings.get(settingkey.KEYBLADE_MIN_STAT)
        self.keyblade_max_stat: int = ui_settings.get(settingkey.KEYBLADE_MAX_STAT)

        self.sora_exp_multiplier: float = ui_settings.get(
            settingkey.SORA_EXP_MULTIPLIER
        )
        self.valor_exp_multiplier: float = ui_settings.get(
            settingkey.VALOR_EXP_MULTIPLIER
        )
        self.wisdom_exp_multiplier: float = ui_settings.get(
            settingkey.WISDOM_EXP_MULTIPLIER
        )
        self.limit_exp_multiplier: float = ui_settings.get(
            settingkey.LIMIT_EXP_MULTIPLIER
        )
        self.master_exp_multiplier: float = ui_settings.get(
            settingkey.MASTER_EXP_MULTIPLIER
        )
        self.final_exp_multiplier: float = ui_settings.get(
            settingkey.FINAL_EXP_MULTIPLIER
        )
        self.summon_exp_multiplier: float = ui_settings.get(
            settingkey.SUMMON_EXP_MULTIPLIER
        )
        self.sora_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.SORA_EXP_CURVE)
        )
        self.valor_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.VALOR_EXP_CURVE)
        )
        self.wisdom_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.WISDOM_EXP_CURVE)
        )
        self.limit_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.LIMIT_EXP_CURVE)
        )
        self.master_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.MASTER_EXP_CURVE)
        )
        self.final_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.FINAL_EXP_CURVE)
        )
        self.summon_exp_curve: expCurve = expCurve.from_name(
            ui_settings.get(settingkey.SUMMON_EXP_CURVE)
        )

        self.as_data_split: bool = ui_settings.get(settingkey.AS_DATA_SPLIT)
        self.chests_match_item: bool = ui_settings.get(settingkey.CHESTS_MATCH_ITEM)
        self.skip_carpet_escape: bool = ui_settings.get(settingkey.SKIP_CARPET_ESCAPE)

        if self.reverse_rando and not self.as_data_split:
            raise SettingsException(
                "Can't run reverse rando without the as/data split code"
            )

        self.enemy_options = makeKHBRSettings(seed_name, ui_settings)

        self.random_seed: str = seed_name
        self.spoiler_log: bool = spoiler_log
        self.ui_version: str = ui_version
        self.create_full_seed_string()
        self.seedHashIcons: list[str] = generate_hash_icons()

        self.statSanity: bool = ui_settings.get(settingkey.STATSANITY)
        self.yeetTheBear: bool = ui_settings.get(settingkey.YEET_THE_BEAR)
        self.chainLogic: bool = ui_settings.get(settingkey.CHAIN_LOGIC)
        self.chainLogicIncludeTerra: bool = ui_settings.get(
            settingkey.CHAIN_LOGIC_TERRA
        )
        self.chainLogicTerraLate: bool = ui_settings.get(
            settingkey.CHAIN_LOGIC_MIN_TERRA
        )
        self.chainLogicMinLength: int = ui_settings.get(settingkey.CHAIN_LOGIC_LENGTH)

        if (
            self.proofDepth in [locationDepth.FirstVisit, locationDepth.FirstBoss]
            and self.chainLogic
        ):
            raise SettingsException(
                "Chain logic is not compatible with first visit proofs"
            )
        if (
            self.storyDepth not in [locationDepth.Anywhere, locationDepth.NonSuperboss]
            and self.chainLogic
        ):
            raise SettingsException(
                "Chain logic is only compatible with visit unlock depth non-data and anywhere"
            )
        if self.chainLogic and self.regular_rando and self.reverse_rando:
            raise SettingsException(
                "Can't do chain logic with both regular and reverse rando"
            )

        self.roxas_abilities_enabled: bool = ui_settings.get(
            settingkey.ROXAS_ABILITIES_ENABLED
        )
        self.disable_final_form: bool = ui_settings.get(settingkey.DISABLE_FINAL_FORM)
        self.block_cor_skip: bool = ui_settings.get(settingkey.BLOCK_COR_SKIP)
        self.block_shan_yu_skip: bool = ui_settings.get(settingkey.BLOCK_SHAN_YU_SKIP)
        self.pr_map_skip: bool = ui_settings.get(settingkey.PR_MAP_SKIP)
        self.atlantica_skip: bool = ui_settings.get(settingkey.ATLANTICA_TUTORIAL_SKIP)
        self.wardrobe_skip: bool = ui_settings.get(settingkey.REMOVE_WARDROBE_ANIMATION)
        self.include_maps: bool = ui_settings.get(settingkey.MAPS_IN_ITEM_POOL)
        self.include_recipes: bool = ui_settings.get(settingkey.RECIPES_IN_ITEM_POOL)
        self.include_accessories: bool = ui_settings.get(
            settingkey.ACCESSORIES_IN_ITEM_POOL
        )
        self.include_armor: bool = ui_settings.get(settingkey.ARMOR_IN_ITEM_POOL)
        self.remove_popups: bool = ui_settings.get(settingkey.REMOVE_POPUPS)

        self.global_jackpot: int = ui_settings.get(settingkey.GLOBAL_JACKPOT)
        self.global_lucky: int = ui_settings.get(settingkey.GLOBAL_LUCKY)
        self.rich_enemies: bool = ui_settings.get(settingkey.RICH_ENEMIES)
        self.unlimited_mp: bool = ui_settings.get(settingkey.UNLIMITED_MP)
        self.fast_urns: bool = ui_settings.get(settingkey.FAST_URNS)

        self.shop_elixirs: bool = ui_settings.get(settingkey.SHOP_ELIXIRS)
        self.shop_recoveries: bool = ui_settings.get(settingkey.SHOP_RECOVERIES)
        self.shop_boosts: bool = ui_settings.get(settingkey.SHOP_BOOSTS)
        self.shop_keyblades: bool = ui_settings.get(settingkey.SHOP_KEYBLADES)
        self.shop_unlocks: int = ui_settings.get(settingkey.SHOP_UNLOCKS)
        self.shop_reports: int = ui_settings.get(settingkey.SHOP_REPORTS)

        self.point_hint_values: dict[str, int] = {
            "proof": ui_settings.get(settingkey.POINTS_PROOF),
            "form": ui_settings.get(settingkey.POINTS_FORM),
            "magic": ui_settings.get(settingkey.POINTS_MAGIC),
            "summon": ui_settings.get(settingkey.POINTS_SUMMON),
            "ability": ui_settings.get(settingkey.POINTS_ABILITY),
            "page": ui_settings.get(settingkey.POINTS_PAGE),
            "report": ui_settings.get(settingkey.POINTS_REPORT),
            "visit": ui_settings.get(settingkey.POINTS_VISIT),
            "bonus": ui_settings.get(settingkey.POINTS_BONUS),
            "complete": ui_settings.get(settingkey.POINTS_COMPLETE),
            "formlv": ui_settings.get(settingkey.POINTS_FORMLV),
            "other": ui_settings.get(settingkey.POINTS_AUX),
            "boss_as": ui_settings.get(settingkey.POINTS_BOSS_AS),
            "boss_datas": ui_settings.get(settingkey.POINTS_BOSS_DATA),
            "boss_sephi": ui_settings.get(settingkey.POINTS_BOSS_SEPHIROTH),
            "boss_terra": ui_settings.get(settingkey.POINTS_BOSS_TERRA),
            "boss_final": ui_settings.get(settingkey.POINTS_BOSS_FINAL),
            "boss_other": ui_settings.get(settingkey.POINTS_BOSS_NORMAL),
            "deaths": ui_settings.get(settingkey.POINTS_DEATH),
            "collection_magic": ui_settings.get(settingkey.POINTS_MAGIC_COLLECT),
            "collection_page": ui_settings.get(settingkey.POINTS_PAGE_COLLECT),
            "collection_pouches": ui_settings.get(settingkey.POINTS_POUCHES_COLLECT),
            "collection_proof": ui_settings.get(settingkey.POINTS_PROOF_COLLECT),
            "collection_form": ui_settings.get(settingkey.POINTS_FORM_COLLECT),
            "collection_summon": ui_settings.get(settingkey.POINTS_SUMMON_COLLECT),
            "collection_ability": ui_settings.get(settingkey.POINTS_ABILITY_COLLECT),
            "collection_report": ui_settings.get(settingkey.POINTS_REPORT_COLLECT),
            "collection_visit": ui_settings.get(settingkey.POINTS_VISIT_COLLECT),
        }

        self.progression_hints: bool = ui_settings.get(settingkey.PROGRESSION_HINTS)
        self.progression_world_complete_bonus: int = ui_settings.get(
            settingkey.PROGRESSION_HINTS_COMPLETE_BONUS
        )
        self.progression_report_bonus: int = ui_settings.get(
            settingkey.PROGRESSION_HINTS_REPORT_BONUS
        )
        self.progression_reveal_all: bool = ui_settings.get(
            settingkey.PROGRESSION_HINTS_REVEAL_END
        )

        self.shop_hintable = (
            (self.shop_unlocks > 0)
            or (self.shop_reports > 0)
            or locationType.Puzzle in include_list
            or locationType.SYNTH in include_list
        )
        prog_points = ProgressionPoints()
        prog_points.set_uncompressed(
            ui_settings.get(settingkey.PROGRESSION_POINT_SELECT)
        )
        self.progression_hint_settings = prog_points.get_points_json()
        num_worlds = (
            len(vanilla_worlds)
            + len(worlds_with_rewards)
            + (1 if self.shop_hintable else 0)
        )
        self.progression_hint_settings["HintCosts"] = prog_points.get_hint_thresholds(
            num_worlds
        )
        self.progression_hint_settings["WorldCompleteBonus"] = [
            self.progression_world_complete_bonus
        ]
        self.progression_hint_settings["ReportBonus"] = [self.progression_report_bonus]
        self.progression_hint_settings["FinalXemnasReveal"] = [
            1 if self.progression_reveal_all else 0
        ]

        self.revealComplete: bool = ui_settings.get(settingkey.REVEAL_COMPLETE)
        self.revealMode: str = ui_settings.get(settingkey.REPORTS_REVEAL)
        self.journal_hints: str = ui_settings.get(settingkey.JOURNAL_HINTS_ABILITIES)

        self.hintable_check_types: list[str] = [
            item_type for item_type in ui_settings.get(settingkey.HINTABLE_CHECKS)
        ]
        self.spoiler_hint_values: list[str] = [
            item_type for item_type in ui_settings.get(settingkey.SPOILER_REVEAL_TYPES)
        ]
        if self.revealComplete:
            self.spoiler_hint_values.append("complete")
        if self.revealMode != "Disabled":
            self.spoiler_hint_values.append(self.revealMode)
            if (
                self.revealMode == "bossreports"
                and ui_settings.get("boss") == "Disabled"
            ):
                raise SettingsException(
                    "Can't use report hint bosses option without boss randomization."
                )
        if (
            self.hintsType == "Spoiler"
            and self.revealMode == "Disabled"
            and self.progression_hints
        ):
            raise SettingsException(
                "Can't use progression hints with full spoiler hints"
            )

        self.hiscore_mode: bool = ui_settings.get(settingkey.SCORE_MODE)

        self.tracker_includes: list[str] = []
        if self.progression_hints:
            self.tracker_includes.append("ProgressionHints")
        if self.vanilla_level_one:
            self.tracker_includes.append("Level1Mode")
        self.tracker_includes.append(level_setting)
        if self.roxas_abilities_enabled:
            self.tracker_includes.append("better_stt")
        if self.as_data_split:
            self.tracker_includes.append("Data Split")
        if len(ui_settings.get(settingkey.STARTING_STORY_UNLOCKS)) < 11:
            self.tracker_includes.append("visit_locking")
        if self.starting_report_count == 13:
            self.tracker_includes.append("library")
        if self.hiscore_mode:
            self.tracker_includes.append("ScoreMode")

        if (
            self.hintsType in ["JSmartee", "Path"]
            and "proof" not in self.hintable_check_types
        ):
            raise SettingsException(
                "Jsmartee and Path hints really need proofs hintable."
            )
        self.important_checks = []
        self.spoiler_reveal_checks = []
        self.populate_check_type_list(self.hintable_check_types, self.important_checks)
        self.populate_check_type_list(
            self.spoiler_hint_values, self.spoiler_reveal_checks
        )

        for check_type in [
            "magic",
            "proof",
            "form",
            "page",
            "summon",
            "visit",
            "ability",
            "other",
            "report",
        ]:
            if check_type not in self.hintable_check_types:
                self.point_hint_values[check_type] = 0

        # making tracker includes use all worlds and
        for l in locationType:
            if l.value in self.enabledLocations:
                if l.value != "Level":  # don't duplicate the level info
                    self.tracker_includes.append(l.value)
            if l.value in self.vanillaLocations:
                if l.value != "Level":  # don't duplicate the level info
                    self.tracker_includes.append(l.value)

        # putting this in the settings object to allow us to turn it off as a safety valve
        self.dummy_forms = True

        self.validateSettings()

    def populate_check_type_list(self, hintable_checks_list, check_list):
        if "magic" in hintable_checks_list:
            check_list += [
                itemType.FIRE,
                itemType.BLIZZARD,
                itemType.THUNDER,
                itemType.CURE,
                itemType.REFLECT,
                itemType.MAGNET,
            ]
        if "proof" in hintable_checks_list:
            check_list += [
                itemType.PROOF_OF_NONEXISTENCE,
                itemType.PROOF_OF_CONNECTION,
                itemType.PROOF_OF_PEACE,
                itemType.PROMISE_CHARM,
            ]
        if "form" in hintable_checks_list:
            check_list += [itemType.FORM, "Anti-Form"]
        if "page" in hintable_checks_list:
            check_list += [itemType.TORN_PAGE]
        if "report" in hintable_checks_list:
            check_list += [itemType.REPORT]
        if "summon" in hintable_checks_list:
            check_list += [itemType.SUMMON]
        if "visit" in hintable_checks_list:
            check_list += [itemType.STORYUNLOCK]
        if "ability" in hintable_checks_list:
            check_list += ["Second Chance", "Once More"]
        if "other" in hintable_checks_list:
            check_list += [
                itemType.TROPHY,
                itemType.MANUFACTORYUNLOCK,
                itemType.OCSTONE,
                itemType.MUNNY_POUCH,
            ]

    def create_full_seed_string(self):
        seed_string_from_all_inputs = (
            self.random_seed
            + str(self.spoiler_log)
            + self.ui_version
            + str(self.ui_settings.settings_string())
        )
        self.full_rando_seed = seed_string_from_all_inputs
        random.seed(seed_string_from_all_inputs)

    def validateSettings(self):
        boss_depths = [
            locationDepth.FirstBoss,
            locationDepth.LastStoryBoss,
            locationDepth.Superbosses,
        ]
        if self.reportDepth == self.proofDepth and self.reportDepth in boss_depths:
            raise SettingsException(
                "Proof depth and report depth can't be set to the same boss category"
            )
        if self.storyDepth == self.proofDepth and self.proofDepth in boss_depths:
            raise SettingsException(
                "Proof depth and visit unlock depth can't be set to the same boss category"
            )
        if self.reportDepth == self.storyDepth and self.reportDepth in boss_depths:
            raise SettingsException(
                "Visit unlock depth and report depth can't be set to the same boss category"
            )

        if locationType.TTR in self.enabledLocations and not self.statSanity:
            raise SettingsException(
                "Enabling Transport to Remembrance when not in Statsanity is incorrect. Enable Statsanity or disable TTR."
            )

        if self.chainLogic:
            if len(self.vanillaLocations) > 0:
                raise SettingsException(
                    "Currently can't do chain logic and vanilla worlds. Sorry about that. "
                )

            if proof.ProofOfNonexistence.id in self.starting_inventory_ids:
                raise SettingsException(
                    "Cannot use chain logic if starting with Proof of Nonexistence"
                )

        if (
            self.ability_pool_option != AbilityPoolOption.DEFAULT
            and len(self.vanillaLocations) > 0
        ):
            pass
            # raise SettingsException("Currently can't do randomized ability pools and vanilla worlds. Sorry about that. ")

        max_reports = len(report.all_reports())
        if self.starting_report_count + self.shop_reports > max_reports:
            raise SettingsException(
                f"Starting Ansem Reports + Ansem Reports in shop is more than {max_reports}"
            )

        max_unlocks = len(storyunlock.all_story_unlocks())
        if len(self.starting_story_unlock_ids) + self.shop_unlocks > max_unlocks:
            raise SettingsException(
                f"Starting Visit Unlocks plus Visit Unlocks in shop is more than {max_unlocks}"
            )

        if self.yeetTheBear:
            if proof.ProofOfNonexistence.id in self.starting_inventory_ids:
                raise SettingsException(
                    "Cannot require Yeet the Bear if starting with Proof of Nonexistence"
                )

            if locationType.HUNDREDAW not in self.enabledLocations:
                raise SettingsException(
                    "Cannot require Yeet the Bear if 100 Acre Wood is Junk or Vanilla"
                )

        if self.proofDepth == locationDepth.Superbosses:
            if (
                locationType.AS not in self.enabledLocations
                and locationType.DataOrg not in self.enabledLocations
            ):
                msg = "Either Absent Silhouettes or Data Organization need to be enabled for superboss-only proof depth"
                raise SettingsException(msg)

    def excluded_levels(self) -> list[int]:
        max_level = self.max_level_checks
        if max_level == 99:
            return self.excludeFrom99
        elif max_level == 50:
            return self.excludeFrom50
        elif max_level == 1:
            return list(range(1, 100))
        else:
            raise SettingsException(f"Incorrect level choice {max_level}")

    def sora_exp(self) -> list[int]:
        return experienceValues.get_sora_exp(
            self.max_level_checks, self.sora_exp_multiplier, self.sora_exp_curve
        )

    def valor_exp(self) -> list[int]:
        return experienceValues.get_form_exp(
            form.ValorForm, self.valor_exp_multiplier, self.valor_exp_curve
        )

    def wisdom_exp(self) -> list[int]:
        return experienceValues.get_form_exp(
            form.WisdomForm, self.wisdom_exp_multiplier, self.wisdom_exp_curve
        )

    def limit_exp(self) -> list[int]:
        return experienceValues.get_form_exp(
            form.LimitForm, self.limit_exp_multiplier, self.limit_exp_curve
        )

    def master_exp(self) -> list[int]:
        return experienceValues.get_form_exp(
            form.MasterForm, self.master_exp_multiplier, self.master_exp_curve
        )

    def final_exp(self) -> list[int]:
        return experienceValues.get_form_exp(
            form.FinalForm, self.final_exp_multiplier, self.final_exp_curve
        )

    def summon_exp(self) -> list[int]:
        return experienceValues.get_summon_exp(
            self.summon_exp_multiplier, self.summon_exp_curve
        )
