from importlib.resources import files

from dungeonsheets import features as feats
from dungeonsheets.content_registry import default_content_registry
from dungeonsheets.yaml_content import load_yaml_background_classes

default_content_registry.add_module(__name__)


class Background:
    name = "Generic background"
    owner = None
    skill_proficiencies = ()
    weapon_proficiencies = ()
    proficiencies_text = ()
    skill_choices = ()
    num_skill_choices = 0
    features = ()
    languages = ()

    def __init__(self, owner=None):
        self.owner = owner
        cls = type(self)
        self.features = tuple([f(owner=self.owner) for f in cls.features])

    def __str__(self):
        return self.name


class Acolyte(Background):
    name = "Acolyte"
    skill_proficiencies = ("insight", "religion")
    languages = ("[choose one]", "[choose one]")
    features = (feats.ShelterOfTheFaithful,)


class Charlatan(Background):
    name = "Charlatan"
    skill_proficiencies = ("deception", "sleight of hand")
    features = (feats.FalseIdentity,)


class Criminal(Background):
    name = "Criminal"
    skill_proficiencies = ("deception", "stealth")
    features = (feats.CriminalContact,)


class Spy(Criminal):
    name = "Spy"


class Entertainer(Background):
    name = "Entertainer"
    skill_proficiencies = ("acrobatics", "performance")
    features = (feats.ByPopularDemand,)


class Gladiator(Entertainer):
    name = "Gladiator"


class Farmer(Background):
    name = "Farmer"
    skill_proficiencies = ("animal handling", "nature")
    proficiencies_text = ("Carpenter's Tools",)
    features = (feats.Tough,)


class FolkHero(Background):
    name = "Folk Hero"
    skill_proficiencies = ("animal handling", "survival")
    features = (feats.RusticHospitality,)


class GuildArtisan(Background):
    name = "Guild Artisan"
    skill_proficiencies = ("insight", "persuasion")
    languages = ("[choose one]", "[choose one]")
    features = (feats.GuildMembership,)


class GuildMerchant(GuildArtisan):
    name = "Guild Merchant"


class Hermit(Background):
    name = "Hermit"
    skill_proficiencies = ("medicine", "religion")
    languages = ("[choose one]",)
    features = (feats.Discovery,)


class Noble(Background):
    name = "Noble"
    skill_proficiencies = ("history", "persuasion")
    languages = ("[choose one]",)
    features = (feats.PositionOfPrivilege,)


class Knight(Noble):
    name = "Knight"


class Outlander(Background):
    name = "Outlander"
    skill_proficiencies = ("athletics", "survival")
    languages = ("[choose one]",)
    features = (feats.Wanderer,)


class RivalIntern(Background):
    """You were an intern at a rival of Acquisitions Incorporated, and you
    gained a healthy respect for nocjusc the job and the franchising
    opportunities. but for the ruth- less and efficient way
    Acquisitions Incorporated goes about its business. Why deal with
    the rest, when you can work for the best?

    Perhaps the rival did not treat you as well as you were hoping, or
    you washed out of that organization. Maybe you hope to leverage
    the knowledge you gained there for an advantage at Acquisitions
    Incorporated. Either way, you're now bringing your talents to the
    company, ready to put your skills lo use.

    """

    name = "Rival Intern"
    skill_proficiencies = ("history", "investigation")
    proficiencies_text = ("One type of artisan's tools",)
    languages = ("[choose one]",)
    features = (feats.InsideInformant,)


class Sage(Background):
    name = "Sage"
    skill_proficiencies = ("arcana", "history")
    languages = ("[choose one]", "[choose one]")
    features = (feats.Researcher,)


class Sailor(Background):
    name = "Sailor"
    skill_proficiencies = ("athletics", "perception")
    features = (feats.ShipsPassage,)


class Pirate(Sailor):
    name = "Pirate"


class Soldier(Background):
    name = "Soldier"
    skill_proficiencies = ("athletics", "intimidation")
    features = (feats.MilitaryRank,)


class Urchin(Background):
    name = "Urchin"
    skill_proficiencies = ("sleight of hand", "stealth")
    features = (feats.CitySecrets,)


# Sword's Coast Adventurers Guide
class CityWatch(Background):
    name = "City Watch"
    skill_proficiencies = ("athletics", "insight")
    languages = ("[choose one]", "[choose one]")
    features = (feats.WatchersEye,)


class ClanCrafter(Background):
    name = "Clan Crafter"
    skill_proficiencies = ("history", "insight")
    languages = ("Dwarvish",)
    features = (feats.RespectOfTheStoutFolk,)


class CloisteredScholar(Background):
    name = "Cloistered Scholar"
    skill_proficiencies = ("history",)
    skill_choices = ("arcana", "nature", "religion")
    num_skill_choices = 1
    languages = ("[choose one]", "[choose one]")
    features = (feats.LibraryAccess,)


class Courtier(Background):
    name = "Courtier"
    skill_proficiencies = ("insight", "persuasion")
    languages = ("[choose one]", "[choose one]")
    features = (feats.CourtFunctionary,)


class FactionAgent(Background):
    name = "Faction Agent"
    skill_proficiencies = ("insight",)
    skill_choices = (
        "animal handling",
        "arcana",
        "deception",
        "history",
        "intimidation",
        "investigation",
        "medicine",
        "nature",
        "perception",
        "performance",
        "persuasion",
        "religion",
        "survival",
    )
    num_skill_choices = 1
    languages = ("[choose one]", "[choose one]")
    features = (feats.SafeHaven,)


class FarTraveler(Background):
    name = "Far Traveler"
    skill_proficiencies = ("insight", "perception")
    languages = ("[choose one]",)
    features = (feats.AllEyesOnYou,)


class Inheritor(Background):
    name = "Inheritor"
    skill_proficiencies = ("survival",)
    skill_choices = ("arcana", "history", "religion")
    num_skill_choices = 1
    languages = ("[choose one]",)
    features = (feats.Inheritance,)


class KnightOfTheOrder(Background):
    name = "Knight of the Order"
    skill_proficiencies = ("persuasion",)
    skill_choices = ("arcana", "history", "nature", "religion")
    num_skill_choices = 1
    languages = ("[choose one]",)
    features = (feats.KnightlyRegard,)


class MercenaryVeteran(Background):
    name = "Mercenary Veteran"
    skill_proficiencies = ("athletics", "persuasion")
    features = (feats.MercenaryLife,)


class UrbanBountyHunter(Background):
    name = "Urban Bounty Hunter"
    skill_proficiencies = ()
    skill_choices = ("Deception", "Insight", "Persuasion", "Stealth")
    num_skill_choices = 2
    features = (feats.EarToTheGround,)


class UthgardtTribeMember(Background):
    name = "Uthgardt Tribe Member"
    skill_profifiencies = ("athletics", "survival")
    languages = ("[choose one]",)
    features = (feats.UthgardtHeritage,)


class WaterdhavianNoble(Background):
    name = "Waterdhavian Noble"
    skill_proficiencies = ("history", "persuasion")
    languages = ("[choose one]",)
    features = (feats.KeptInStyle,)


class Faceless(Background):
    """Being who you are, you could never be a hero.
    Wether due to your class, your people, your family, or your sins, something
    about you prevents you from effectively pursuing the path you've chosen.
    Even so, that doesn't stop you. You've left your old face behind, taking on
    a new persona, becoming something more.
    Characters with the faceless background don a disguise (literally or
    otherwise) as they adventuree. This persona might be dramatic or subtle. In
    a way, though, many characters have such larger than life personalities.
    Therefore, this background largely focuses on detailing the hero behind the
    mask.
    """

    name = "Faceless"
    skill_proficiencies = ("Deception", "Intimidation")
    features = (feats.FacelessPersona, feats.DualPersonalities)


_yaml_loaded = False


_LEGACY_BACKGROUNDS = {
    name: obj
    for name, obj in list(globals().items())
    if isinstance(obj, type) and issubclass(obj, Background) and obj is not Background
}

# Remove concrete background class bindings so first access triggers __getattr__
# and loads YAML-backed classes before exposing legacy fallbacks.
for _name in _LEGACY_BACKGROUNDS:
    globals().pop(_name, None)


def _load_yaml_content():
    global _yaml_loaded
    if _yaml_loaded:
        return

    generated = load_yaml_background_classes(
        files("dungeonsheets.data").joinpath("backgrounds.yaml"),
        Background,
        feats,
        module=__name__,
    )

    globals().update(_LEGACY_BACKGROUNDS)
    globals().update(generated)

    globals()["PHB_backgrounds"] = [
        globals()[name]
        for name in (
            "Acolyte",
            "Charlatan",
            "Criminal",
            "Spy",
            "Entertainer",
            "Gladiator",
            "Farmer",
            "FolkHero",
            "GuildArtisan",
            "GuildMerchant",
            "Hermit",
            "Noble",
            "Knight",
            "Outlander",
            "Sage",
            "Sailor",
            "Pirate",
            "Soldier",
            "Urchin",
        )
    ]
    globals()["SCAG_backgrounds"] = [
        globals()[name]
        for name in (
            "CityWatch",
            "ClanCrafter",
            "CloisteredScholar",
            "Courtier",
            "FactionAgent",
            "FarTraveler",
            "Inheritor",
            "KnightOfTheOrder",
            "MercenaryVeteran",
            "UrbanBountyHunter",
            "UthgardtTribeMember",
            "WaterdhavianNoble",
        )
    ]
    globals()["available_backgrounds"] = (
        globals()["PHB_backgrounds"] + globals()["SCAG_backgrounds"]
    )

    _yaml_loaded = True


def __getattr__(name):
    _load_yaml_content()
    try:
        return globals()[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


def __dir__():
    _load_yaml_content()
    return sorted(globals())


_PUBLIC_EXPORTS = (
    "Acolyte",
    "Charlatan",
    "Criminal",
    "Spy",
    "Entertainer",
    "Gladiator",
    "Farmer",
    "FolkHero",
    "GuildArtisan",
    "GuildMerchant",
    "Hermit",
    "Noble",
    "Knight",
    "Outlander",
    "Sage",
    "Sailor",
    "Pirate",
    "Soldier",
    "Urchin",
    "CityWatch",
    "ClanCrafter",
    "CloisteredScholar",
    "Courtier",
    "FactionAgent",
    "FarTraveler",
    "Inheritor",
    "KnightOfTheOrder",
    "MercenaryVeteran",
    "UrbanBountyHunter",
    "UthgardtTribeMember",
    "WaterdhavianNoble",
    "PHB_backgrounds",
    "SCAG_backgrounds",
    "available_backgrounds",
)

__all__ = _PUBLIC_EXPORTS
