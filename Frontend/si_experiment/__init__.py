from otree.api import *
import random

doc = """
The impact of social identity on reliance / trust in AI
"""

class C(BaseConstants):
    NAME_IN_URL = 'si_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


# FUNCTIONS
def make_field(label):
    return models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        label=label,
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )


def shuffle_form_fields(fields, blocksize=3, subblocks=True):
    form_fields = fields
    blocksize = blocksize

    blocks = [form_fields[i:i + blocksize] for i in range(0, len(form_fields), blocksize)]
    random.shuffle(blocks)
    if subblocks:
        for subblock in blocks:
            random.shuffle(subblock)
    form_fields = [formfield for subblock in blocks for formfield in subblock]
    return form_fields


def creating_session(subsession):
    for player in subsession.get_players():
        participant = player.participant
        pers_inno = ["pers_inno1", "pers_inno2", "pers_inno3", "pers_inno4"]
        random.shuffle(pers_inno)
        participant.pers_inno_order = pers_inno


class Player(BasePlayer):
    # Treatments: Baseline, Accuracy, Developer and Accuracy
    treatment = models.IntegerField()

    # Preliminary Questions
    age = models.IntegerField(label="Bitte geben Sie Ihr Alter an.", min=18, max=99, blank=True)
    sex = models.IntegerField(choices=[[0, "Divers"], [1, "Weiblich"], [2, "Männlich"]],
                              widget=widgets.RadioSelectHorizontal, label="Bitte geben Sie Ihr Geschlecht an.",
                              blank=True)
    nationality = models.BooleanField(choices=[[True, "Deutsch"], [False, "Nichtdeutsch"]],
                                      widget=widgets.RadioSelectHorizontal,
                                      label="Bitte geben Sie an, ob Ihre Nationalität Deutsch ist.", blank=True)
    migration_bg = models.BooleanField(choices=[[True, "Ja, ich habe einen Migrationshintergrund"],
                                                [False, "Nein, ich habe keinen Migrationshintergrund"]],
                                       widget=widgets.RadioSelect,
                                       label="Bitte geben Sie an, ob Sie einen Migrationshintergrund besitzen.",
                                       blank=True)
    student = models.BooleanField(choices=[[True, "Ja"],
                                           [False, "Nein"]],
                                  widget=widgets.RadioSelectHorizontal, label="Bitte geben Sie an, ob Sie studieren.",
                                  blank=True)
    # todo: Tbd
    job = models.IntegerField(choices=[[0, "Baden-Württemberg"], [1, "Bayern"], [2, "Berlin"], [3, "Brandenburg"],
                                       [4, "Bremen"], [5, "Hamburg"], [6, "Hessen"], [7, "Mecklenburg-Vorpommern"],
                                       [8, "Niedersachsen"], [9, "Nordrhein-Westfalen"], [10, "Rheinland-Pfalz"],
                                       [11, "Saarland"],
                                       [12, "Sachsen-Anhalt"], [13, "Sachsen"], [14, "Schleswig-Holstein"],
                                       [15, "Thüringen"]],
                              label="TBD: Bitte geben Sie an, in welchem Arbeitsbereich Sie arbeiten bzw. studieren.",
                              blank=True)

    pol_views = models.IntegerField(blank=True)

    importance_sex = models.IntegerField(label="Das Geschlecht", blank=True)
    importance_migration_bg = models.IntegerField(label="Der Migrationshintergrund", blank=True)
    importance_pol_views = models.IntegerField(label="Die politische Einstellung", blank=True)

    soc_norms = make_field("Ich tue immer mein Bestes, um gesellschaftliche Normen zu befolgen.")

    # tech-savyness
    pers_inno1 = make_field(
        "Wenn ich von einer neuen Technologie hören würde, würde ich nach Möglichkeiten suchen, damit zu experimentieren.")
    pers_inno2 = make_field(
        "Unter meinen Kolleg*innen bzw. Kommiliton*innen bin ich in der Regel die/der erste, die/der neue Technologie ausprobiert.")
    pers_inno3 = make_field("Im Allgemeinen zögere ich davor, neue Technologie auszuprobieren.")
    pers_inno4 = make_field("Ich experimentiere gerne mit neuer Technologie.")

    # task
    confidence = make_field(
        "Bitte sagen Sie uns, wie sicher Sie sich bei der soeben getroffenen Vorhersage des Immobilienpreises fühlen. ")
    confidence_rev = make_field(
        "Bitte sagen Sie uns, wie sicher Sie sich bei der soeben getroffenen Vorhersage des Immobilienpreises fühlen. ")

    # todo immobilien-expertise, risikoaversion
    immo_exp = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="TBD: Bitte geben Sie an, wie gut Ihre Erfahrungen mit Immobilien sind.")
    risk_aver = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="TBD: Wie risikoavers sind Sie?")

    # revision
    revision = models.FloatField()
    confRevision = models.IntegerField(label="", widget=widgets.RadioSelectHorizontal,
                                        choices=[1, 2, 3, 4, 5])

    ###################
    # algorithm items #
    ###################
    transparency = make_field("Ich verstehe, wie der Algorithmus zu seiner Empfehlung kommt.")

    anthro_natural = make_field("Der Algorithmus ist für mich natürlich.")
    anthro_human = make_field("Der Algorithmus ist für mich menschenähnlich.")
    # attention check
    anthro_conscious = make_field("Der Algorithmus ist für mich ohne Bewusstsein.")
    anthro_lifelike = make_field("Der Algorithmus ist für mich lebensähnlich.")

    # trust
    cog_trust1 = make_field("Der Algorithmus ist kompetent und effektiv bei der Vorhersage der Immobilienpreise.")
    cog_trust2 = make_field("Der Algorithmus erfüllt seine Aufgabe, die Immobilienpreise vorherzusagen, sehr gut.")
    cog_trust3 = make_field(
        "Insgesamt ist Der Algorithmus ein fähiges und kompetentes Werkzeug für die Vorhersage der Immobilienpreise.")
    integ_trust1 = make_field("Der Algorithmus gibt unvoreingenommene Empfehlungen.")
    # attention check 1
    integ_trust2 = make_field("Der Algorithmus ist unehrlich.")
    integ_trust3 = make_field("Ich halte diesen Algorithmus für integer.")
    # attention check 2
    emo_trust1 = make_field(
        "Ich fühle mich unsicher, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.")
    emo_trust2 = make_field(
        "Ich fühle mich wohl, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.")
    emo_trust3 = make_field(
        "Ich fühle mich zufrieden, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.")


# PAGES
class Intro(Page):
    pass


class PreQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["importance_sex", "importance_migration_bg", "importance_pol_views",
                       "age", "sex", "nationality", "migration_bg", "student", "job", "immo_exp", "risk_aver",
                       "pol_views", "soc_norms"]
        form_fields += player.participant.pers_inno_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        demo = ["age", "sex", "nationality", "migration_bg", "student", "job", "immo_exp", "risk_aver", ]
        return dict(
            demo=demo,
        )


class Task(Page):
    pass


class WTP(Page):
    pass


class Revision(Page):
    form_model = 'player'
    form_fields = ["revision", "confRevision"]


class PostQuestions(Page):
    pass


class End(Page):
    pass


# Intro, PreQuestions,
# , PostQuestions, End
page_sequence = [
    Task,
    WTP,
    Revision]
