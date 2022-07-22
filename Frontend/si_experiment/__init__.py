from otree.api import *
import pandas as pd
import random

doc = """
The impact of social identity on reliance / trust in AI
"""

class C(BaseConstants):
    NAME_IN_URL = 'si_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    CHOICES = ["Geschlecht", "Migrationshintergrund", "Politische Ansichten"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

#todo remove all blank=True
# FUNCTIONS
def make_field(label):
    return models.IntegerField(
        choices=[1, 2, 3, 4, 5],
        label=label,
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )

def make_rank_field(label):
    return models.StringField(choices=C.CHOICES, label=label, blank=True)

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
        post_questions = [
            "anthro1", "anthro2", "anthro3",
            "cog_trust1", "cog_trust2", "cog_trust3",
            "integ_trust1", "integ_trust2", "integ_trust3",
            "emo_trust1", "emo_trust2", "emo_trust3",
        ]
        random.shuffle(pers_inno)
        # True = Immo task first
        # False = Credit task first
        tasks_order = True #random.choice([True, False])
        post_questions = shuffle_form_fields(post_questions, 3, True)

        participant.pers_inno_order = pers_inno
        participant.post_questions_order = post_questions
        participant.tasks_order = tasks_order
        participant.apartment_row = random.randint(0, 9)
        participant.lender_row = random.randint(0, 9)

class Player(BasePlayer):
    # intro data
    is_mobile = models.BooleanField()
    consent = models.BooleanField(choices=["Ich möchte an der Studie teilnehmen."],
                                  label="Durch das Ankreuzen des Kästchens erkläre ich mich mit der Teilnahme an der Studie einverstanden.", blank=True)

    # Treatments: Baseline, Accuracy, Developer and Accuracy
    treatment = models.IntegerField()

    # Preliminary Questions
    age = models.IntegerField(label="Bitte geben Sie Ihr Alter an.", min=18, max=99, blank=True)
    sex = models.IntegerField(choices=[[0, "Divers"], [1, "Weiblich"], [2, "Männlich"]],
                              widget=widgets.RadioSelect, label="Bitte geben Sie Ihr Geschlecht an.", blank=True)
    nationality = models.BooleanField(choices=[[True, "Deutsch"], [False, "Nichtdeutsch"]],
                              widget=widgets.RadioSelectHorizontal, label="Bitte geben Sie an, ob Ihre Nationalität Deutsch ist.", blank=True)
    migration_bg = models.BooleanField(choices=[[True, "Ja, ich habe einen Migrationshintergrund"],
                                                [False, "Nein, ich habe keinen Migrationshintergrund"]],
                                       widget=widgets.RadioSelect, label="Bitte geben Sie an, ob Sie einen Migrationshintergrund besitzen.", blank=True)
    # student = models.BooleanField(choices=[[True, "Ja"],
    #                                        [False, "Nein"]],
    #                               widget=widgets.RadioSelectHorizontal, label="Bitte geben Sie an, ob Sie studieren.", blank=True)
    job_status = models.IntegerField(
        choices=[[0, "Vollzeitbeschäftigung"], [1, "Teilzeitbeschäftigung"], [2, "Selbstständig"],
                 [3, "Hausfrau/mann"], [4, "Student"], [5, "Rentner"]],
        label="Wie ist Ihr derzeitiger Beschäftigungsstatus?", blank=True)

    # todo: Tbd
    job = models.IntegerField(choices=[[0,"Baden-Württemberg"],[1,"Bayern"],[2,"Berlin"],[3,"Brandenburg"],
                                          [4,"Bremen"],[5,"Hamburg"],[6,"Hessen"],[7,"Mecklenburg-Vorpommern"],
                                          [8,"Niedersachsen"],[9,"Nordrhein-Westfalen"],[10,"Rheinland-Pfalz"],[11,"Saarland"],
                                          [12,"Sachsen-Anhalt"],[13,"Sachsen"],[14,"Schleswig-Holstein"],[15,"Thüringen"]],
                                 label="TBD: Bitte geben Sie an, in welchem Arbeitsbereich Sie arbeiten bzw. studieren.", blank=True)


    pol_views = models.IntegerField(choices=[[0,"0 (ganz links)"],[1,1],[2,2],[3,3],
                                          [4,4],[5,5],[6,6],[7,7],
                                          [8,8],[9,9],[10,"10 (ganz rechts)"]],
                                        label="In der Politik reden die Leute oft von 'links' und 'rechts', wenn es darum geht, unterschiedliche politische Einstellungen zu kennzeichnen. "
                                          "Wenn Sie an Ihre eigenen politischen Ansichten denken: Wo würden Sie diese Ansichten einstufen?",blank=True)

    importance_sex = make_field("Das Geschlecht")
    importance_migration_bg = make_field("Der Migrationshintergrund")
    importance_pol_views = make_field("Die politische Einstellung")
    soc_distance_rank1 = make_rank_field("1. Platz")
    soc_distance_rank2 = make_rank_field("2. Platz")
    soc_distance_rank3 = make_rank_field("3. Platz")

    soc_distance1 = make_field("Der Entwickler könnte ähnliche Ansichten haben wie ich.")
    soc_distance2 = make_field("Der Entwickler könnte ähnliche Werte haben wie ich.")
    soc_distance3 = make_field("Ich könnte zur gleichen Gruppe gehören wie der Entwickler.")
    soc_distance4 = make_field("Ich bin eine ähnlicher Mensch wie der Entwickler.")

    soc_norms = make_field("Ich tue immer mein Bestes, um gesellschaftliche Normen zu befolgen.")

    # tech-savyness
    pers_inno1 = make_field("Wenn ich von einer neuen Technologie hören würde, würde ich nach Möglichkeiten suchen, damit zu experimentieren.")
    pers_inno2 = make_field("Unter meinen Kolleg*innen bzw. Kommiliton*innen bin ich in der Regel die/der erste, die/der neue Technologie ausprobiert.")
    pers_inno3 = make_field("Im Allgemeinen zögere ich davor, neue Technologie auszuprobieren.")
    pers_inno4 = make_field("Ich experimentiere gerne mit neuer Technologie.")

    # task1
    task1Estimate = models.FloatField()
    conf1Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # task2
    task2Estimate = models.FloatField()
    conf2Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # perceived accuracy of AI
    perc_acc = models.FloatField()

    # todo immobilien-expertise
    # todo credit default expertise
    immo_exp = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="TBD: Bitte geben Sie an, wie gut Ihre Erfahrungen mit Immobilien sind.", blank=True)
    credit_exp = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="TBD: Bitte geben Sie an, wie gut Ihre Erfahrungen mit Krediten sind.", blank=True)

    risk_aver = models.IntegerField(
        choices=[[0,"0 (völlig risikoscheu)"],[1,1],[2,2],[3,3],
                                          [4,4],[5,5],[6,6],[7,7],
                                          [8,8],[9,9],[10,"10 (sehr risikofreudig)"]],
        label="Bitte geben Sie an, wie risikobereit oder risikoscheu Sie im Allgemeinen sind. Bitte nutzen Sie eine Skala von 0 bis 10, wobei 0 'völlig risikoscheu' und 10 'sehr risikofreudig' bedeutet.",
        blank=True)

    # Revision
    revision = models.FloatField()
    confRevision = make_field("Ich bin von meiner Schätzung überzeugt.")
    click_sex_open, click_sex_close = models.IntegerField(), models.IntegerField()
    click_migration_bg_open, click_migration_bg_close = models.IntegerField(), models.IntegerField()
    click_pol_views_open, click_pol_views_close = models.IntegerField(), models.IntegerField()
    click_acc_open, click_acc_close = models.IntegerField(), models.IntegerField()

    # todo add items for credit task
    ###################
    # algorithm items #
    ###################
    transparency = make_field("Ich verstehe, wie der Algorithmus zu seiner Empfehlung kommt.")

    anthro1 = make_field("Der Algorithmus ist für mich natürlich.")
    anthro2 = make_field("Der Algorithmus ist für mich menschenähnlich.")
    anthro3 = make_field("Der Algorithmus ist für mich lebensähnlich.")

    # trust
    cog_trust1 = make_field("Der Algorithmus ist kompetent und effektiv bei der Vorhersage der Immobilienpreise.")
    cog_trust2 = make_field("Der Algorithmus erfüllt seine Aufgabe, die Immobilienpreise vorherzusagen, sehr gut.")
    cog_trust3 = make_field("Insgesamt ist der Algorithmus ein fähiges und kompetentes Werkzeug für die Vorhersage der Immobilienpreise.")
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
    form_model = 'player'
    form_fields = ['is_mobile', 'consent']


class PreQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["importance_sex", "importance_migration_bg", "importance_pol_views",
                       "age", "sex", "nationality", "migration_bg", "job_status", "job", "immo_exp", "credit_exp", "risk_aver",
                       "pol_views", "soc_norms"]
        form_fields += player.participant.pers_inno_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # removed "sex", "migration_bg"
        demo = ["age", "nationality", "job_status", "job", "immo_exp", "credit_exp", "risk_aver",]
        return dict(
            demo=demo,
        )


class Task(Page):
    form_model = 'player'
    # todo add "estimate",
    # todo input fields according to immo or credit task sequence
    form_fields = ["task1Estimate", "conf1Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        apartments = pd.read_csv("../RealEstate/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
            'floor', 'n_rooms', 'sq_meters', 'construction_year',
            'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])
        tasks_order = player.participant.tasks_order
        return dict(tasks_order=tasks_order,
                    apartment=apartment)

class PercAccuracy(Page):
    form_model = 'player'
    form_fields = ["perc_acc"]

class WTP(Page):
    form_model = "player"
    # form_fields = ["wtp"]

class Revision(Page):
    form_model = 'player'
    form_fields = ["revision", "confRevision",
                   "click_sex_open", "click_sex_close",
                   "click_migration_bg_open", "click_migration_bg_close",
                   "click_pol_views_open", "click_pol_views_close",
                   "click_acc_open", "click_acc_close"]

class PostQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance1", "soc_distance2", "soc_distance3", "soc_distance4",
                       "soc_distance_rank1","soc_distance_rank2","soc_distance_rank3","transparency"]
        form_fields += player.participant.post_questions_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        ranks = ["soc_distance_rank1","soc_distance_rank2","soc_distance_rank3"]
        return dict(
            ranks=ranks,
        )

    # @staticmethod
    # def error_message(player: Player, values):
    #     choices = [values['soc_distance_rank1'], values['soc_distance_rank2'], values['soc_distance_rank3']]
    #     # set() gives you distinct elements. if a list's length is different from its
    #     # set length, that means it must have duplicates.
    #     if len(set(choices)) != len(choices):
    #         return "Sie können nicht dasselbe Element mehrfach auswählen."

class Stage2(Page):
    pass

class Task2(Page):
    form_model = 'player'
    # todo add "estimate",
    # todo input fields according to immo or credit task sequence
    form_fields = ["conf2Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        tasks_order = player.participant.tasks_order
        return dict(tasks_order=tasks_order)

class PercAccuracy2(Page):
    form_model = 'player'
    form_fields = ["perc_acc"]

class Revision2(Page):
    form_model = 'player'
    form_fields = ["revision", "confRevision",
                   "click_sex_open", "click_sex_close",
                   "click_migration_bg_open", "click_migration_bg_close",
                   "click_pol_views_open", "click_pol_views_close",
                   "click_acc_open", "click_acc_close"]

class PostQuestions2(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance1", "soc_distance2", "soc_distance3", "soc_distance4",
                       "soc_distance_rank1","soc_distance_rank2","soc_distance_rank3","transparency"]
        form_fields += player.participant.post_questions_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        ranks = ["soc_distance_rank1","soc_distance_rank2","soc_distance_rank3"]
        return dict(
            ranks=ranks,
        )

    # @staticmethod
    # def error_message(player: Player, values):
    #     choices = [values['soc_distance_rank1'], values['soc_distance_rank2'], values['soc_distance_rank3']]
    #     # set() gives you distinct elements. if a list's length is different from its
    #     # set length, that means it must have duplicates.
    #     if len(set(choices)) != len(choices):
    #         return "Sie können nicht dasselbe Element mehrfach auswählen."

class End(Page):
    pass

page_sequence = [Intro,
                 PreQuestions,
                 Task,
                 PercAccuracy,
                 WTP,
                 Revision,
                 PostQuestions,
                 Stage2,
                 Task2,
                 PercAccuracy2,
                 Revision2,
                 PostQuestions2,
                 End]
