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


# todo remove all blank=True
# FUNCTIONS
def make_field(label):
    return models.IntegerField(
        choices=[1, 2, 3, 4, 5],
        label=label,
        widget=widgets.RadioSelectHorizontal,
        blank=True
    )


def format_german_number(number, precision=0):
    # build format string
    format_str = '{{:,.{}f}}'.format(precision)

    # make number string
    number_str = format_str.format(number)

    # replace chars
    return number_str.replace(',', 'X').replace('.', ',').replace('X', '.')


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

        # treatment and question/task order randomization
        treatments = ["none", "dev", "acc", "both"]
        pers_inno = ["pers_inno1", "pers_inno2", "pers_inno3", "pers_inno4"]
        post_questions_t1 = [
            "anthro_t1_1", "anthro_t1_2", "anthro_t1_3",
            "cog_trust_t1_1", "cog_trust_t1_2", "cog_trust_t1_3",
            "integ_trust_t1_1", "integ_trust_t1_2", "integ_trust_t1_3",
            "emo_trust_t1_1", "emo_trust_t1_2", "emo_trust_t1_3",
        ]
        post_questions_t2 = [
            "anthro_t2_1", "anthro_t2_2", "anthro_t2_3",
            "cog_trust_t2_1", "cog_trust_t2_2", "cog_trust_t2_3",
            "integ_trust_t2_1", "integ_trust_t2_2", "integ_trust_t2_3",
            "emo_trust_t2_1", "emo_trust_t2_2", "emo_trust_t2_3",
        ]
        random.shuffle(pers_inno)
        tasks_order = random.choice([True, False])  # True = Immo task first
        post_questions_t1 = shuffle_form_fields(post_questions_t1, 3, True)
        post_questions_t2 = shuffle_form_fields(post_questions_t2, 3, True)
        participant.treatment = random.choice(treatments)
        participant.pers_inno_order = pers_inno
        participant.post_questions_order_t1 = post_questions_t1
        participant.post_questions_order_t2 = post_questions_t2
        participant.tasks_order = tasks_order

        # task object randomization
        participant.apartment_row = random.randint(0, 9)
        participant.lender_row = random.randint(0, 9)

        # dev profile randomization
        dev_rows = [0, 1, 2]
        participant.dev_row1 = random.choice(dev_rows)
        dev_rows.remove(participant.dev_row1)
        participant.dev_row2 = random.choice(dev_rows)

        # dev vs acc order in display (relevant for treatment=both only)
        if participant.treatment == "both":
            info_first = random.choice(["dev", "acc"])
        else:
            info_first = "not_applicable"
        participant.info_first = info_first

        # post question task adaption
        if tasks_order:
            t1_str = "Immobilienpreise"
            t2_str = "Kreditausfallwahrscheinlichkeiten"
        else:
            t1_str = "Kreditausfallwahrscheinlichkeiten"
            t2_str = "Immobilienpreise"
        participant.t1_str = t1_str
        participant.t2_str = t2_str


class Player(BasePlayer):
    # intro data
    is_mobile = models.BooleanField()
    consent = models.BooleanField(choices=["Ich möchte an der Studie teilnehmen."],
                                  label="Durch das Ankreuzen des Kästchens erkläre ich mich mit der Teilnahme an der Studie einverstanden.",
                                  blank=True)

    # Preliminary Questions
    age = models.IntegerField(label="Bitte geben Sie Ihr Alter an.", min=18, max=99, blank=True)
    sex = models.IntegerField(choices=[[0, "Divers"], [1, "Weiblich"], [2, "Männlich"]],
                              widget=widgets.RadioSelect, label="Bitte geben Sie Ihr Geschlecht an.", blank=True)
    nationality = models.BooleanField(choices=[[True, "Deutsch"], [False, "Nichtdeutsch"]],
                                      widget=widgets.RadioSelectHorizontal,
                                      label="Bitte geben Sie an, ob Ihre Nationalität Deutsch ist.", blank=True)
    migration_bg = models.BooleanField(choices=[[True, "Ja, ich habe einen Migrationshintergrund"],
                                                [False, "Nein, ich habe keinen Migrationshintergrund"]],
                                       widget=widgets.RadioSelect,
                                       label="Bitte geben Sie an, ob Sie einen Migrationshintergrund besitzen.",
                                       blank=True)
    # student = models.BooleanField(choices=[[True, "Ja"],
    #                                        [False, "Nein"]],
    #                               widget=widgets.RadioSelectHorizontal, label="Bitte geben Sie an, ob Sie studieren.", blank=True)
    job_status = models.IntegerField(
        choices=[[0, "Vollzeitbeschäftigung"], [1, "Teilzeitbeschäftigung"], [2, "Selbstständig"],
                 [3, "Hausfrau/mann"], [4, "Studium"], [5, "Rente"]],
        label="Wie ist Ihr derzeitiger Beschäftigungsstatus?", blank=True)

    # job = models.IntegerField(choices=[[0, "Baden-Württemberg"], [1, "Bayern"], [2, "Berlin"], [3, "Brandenburg"],
    #                                    [4, "Bremen"], [5, "Hamburg"], [6, "Hessen"], [7, "Mecklenburg-Vorpommern"],
    #                                    [8, "Niedersachsen"], [9, "Nordrhein-Westfalen"], [10, "Rheinland-Pfalz"],
    #                                    [11, "Saarland"],
    #                                    [12, "Sachsen-Anhalt"], [13, "Sachsen"], [14, "Schleswig-Holstein"],
    #                                    [15, "Thüringen"]],
    #                           label="TBD: Bitte geben Sie an, in welchem Arbeitsbereich Sie arbeiten bzw. studieren.",
    #                           blank=True)

    pol_views = models.IntegerField(choices=[[0, "0 (ganz links)"], [1, 1], [2, 2], [3, 3],
                                             [4, 4], [5, 5], [6, 6], [7, 7],
                                             [8, 8], [9, 9], [10, "10 (ganz rechts)"]],
                                    label="In der Politik reden die Leute oft von 'links' und 'rechts', wenn es darum geht, unterschiedliche politische Einstellungen zu kennzeichnen. "
                                          "Wenn Sie an Ihre eigenen politischen Ansichten denken: Wo würden Sie diese Ansichten einstufen?",
                                    blank=True)

    importance_sex = make_field("Das Geschlecht")
    importance_migration_bg = make_field("Der Migrationshintergrund")
    importance_pol_views = make_field("Die politische Einstellung")

    # social distance var -- task 1
    soc_distance_rank_t1_1 = make_rank_field("1. Platz")
    soc_distance_rank_t1_2 = make_rank_field("2. Platz")
    soc_distance_rank_t1_3 = make_rank_field("3. Platz")

    soc_distance_t1_1 = make_field("Der Entwickler könnte ähnliche Ansichten haben wie ich.")
    soc_distance_t1_2 = make_field("Der Entwickler könnte ähnliche Werte haben wie ich.")
    soc_distance_t1_3 = make_field("Ich könnte zur gleichen Gruppe gehören wie der Entwickler.")
    soc_distance_t1_4 = make_field("Ich bin eine ähnlicher Mensch wie der Entwickler.")

    # social distance var -- task 2
    soc_distance_rank_t2_1 = make_rank_field("1. Platz")
    soc_distance_rank_t2_2 = make_rank_field("2. Platz")
    soc_distance_rank_t2_3 = make_rank_field("3. Platz")

    soc_distance_t2_1 = make_field("Der Entwickler könnte ähnliche Ansichten haben wie ich.")
    soc_distance_t2_2 = make_field("Der Entwickler könnte ähnliche Werte haben wie ich.")
    soc_distance_t2_3 = make_field("Ich könnte zur gleichen Gruppe gehören wie der Entwickler.")
    soc_distance_t2_4 = make_field("Ich bin eine ähnlicher Mensch wie der Entwickler.")

    soc_norms = make_field("Ich tue immer mein Bestes, um gesellschaftliche Normen zu befolgen.")

    # tech-savyness
    pers_inno1 = make_field(
        "Wenn ich von einer neuen Technologie hören würde, würde ich nach Möglichkeiten suchen, damit zu experimentieren.")
    pers_inno2 = make_field(
        "Unter meinen Kolleg*innen bzw. Kommiliton*innen bin ich in der Regel die/der erste, die/der neue Technologie ausprobiert.")
    pers_inno3 = make_field("Im Allgemeinen zögere ich davor, neue Technologie auszuprobieren.")
    pers_inno4 = make_field("Ich experimentiere gerne mit neuer Technologie.")

    # task1
    task1Estimate = models.FloatField()
    conf1Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # task2
    task2Estimate = models.FloatField()
    conf2Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # perceived accuracy of AI -- task 1 and 2
    perc_acc = models.FloatField()
    perc_acc2 = models.FloatField()

    # wtp -- task 1 and 2
    wtp = models.FloatField()
    wtp2 = models.FloatField()

    immo_exp = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="Bitte geben Sie an, wie gut Ihre Erfahrungen mit Immobilien sind.", blank=True)
    credit_exp = models.IntegerField(
        choices=[[0, "Keine Erfahrungen"], [1, "Wenige Erfahrungen"], [2, "Einige Erfahrungen"],
                 [3, "Viel Erfahrungen"]],
        label="Bitte geben Sie an, wie gut Ihre Erfahrungen mit Krediten sind.", blank=True)

    risk_aver = models.IntegerField(
        choices=[[0, "0 (äußerst risikoscheu)"], [1, 1], [2, 2], [3, 3],
                 [4, 4], [5, 5], [6, 6], [7, 7],
                 [8, 8], [9, 9], [10, "10 (äußerst risikofreudig)"]],
        label="Bitte geben Sie an, wie risikobereit oder risikoscheu Sie im Allgemeinen sind. Bitte nutzen Sie eine Skala von 0 bis 10, wobei 0 'äußerst risikoscheu' und 10 'äußerst risikofreudig' bedeutet.",
        blank=True)

    # Revision 1
    revision = models.FloatField()
    confRevision = make_field("Ich bin von meiner Schätzung überzeugt.")
    click_sex_open, click_sex_close = models.IntegerField(), models.IntegerField()
    click_migration_bg_open, click_migration_bg_close = models.IntegerField(), models.IntegerField()
    click_pol_views_open, click_pol_views_close = models.IntegerField(), models.IntegerField()
    click_acc_open, click_acc_close = models.IntegerField(), models.IntegerField()

    # Revision 2
    revision2 = models.FloatField()
    confRevision2 = make_field("Ich bin von meiner Schätzung überzeugt.")
    click_sex_open2, click_sex_close2 = models.IntegerField(), models.IntegerField()
    click_migration_bg_open2, click_migration_bg_close2 = models.IntegerField(), models.IntegerField()
    click_pol_views_open2, click_pol_views_close2 = models.IntegerField(), models.IntegerField()
    click_acc_open2, click_acc_close2 = models.IntegerField(), models.IntegerField()

    # TASK 2 post questions

    transparency_t1 = make_field("Ich verstehe, wie diese KI zu ihrer Empfehlung kommt.")

    anthro_t1_1 = make_field("Diese KI ist für mich natürlich.")
    anthro_t1_2 = make_field("Diese KI ist für mich menschenähnlich.")
    anthro_t1_3 = make_field("Diese KI ist für mich lebensähnlich.")

    cog_trust_t1_1 = make_field("Diese KI ist kompetent und effektiv bei der Vorhersage.")  # der Immobilienpreise
    cog_trust_t1_2 = make_field("Diese KI erfüllt ihre Aufgabe der Vorhersage sehr gut.")  # , die Immobilienpreise vorherzusagen,
    cog_trust_t1_3 = make_field(
        "Insgesamt ist diese KI ein fähiges und kompetentes Werkzeug für die Vorhersage.")  # der Immobilienpreise
    integ_trust_t1_1 = make_field("Diese KI gibt unvoreingenommene Empfehlungen.")
    # attention check 1
    integ_trust_t1_2 = make_field("Diese KI ist unehrlich.")
    integ_trust_t1_3 = make_field("Ich halte diese KI für integer.")
    # attention check 2
    emo_trust_t1_1 = make_field(
        "Ich fühle mich unsicher, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise
    emo_trust_t1_2 = make_field(
        "Ich fühle mich wohl, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise
    emo_trust_t1_3 = make_field(
        "Ich fühle mich zufrieden, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise

    # TASK 2 post questions

    transparency_t2 = make_field("Ich verstehe, wie diese KI zu ihrer Empfehlung kommt.")

    anthro_t2_1 = make_field("Diese KI ist für mich natürlich.")
    anthro_t2_2 = make_field("Diese KI ist für mich menschenähnlich.")
    anthro_t2_3 = make_field("Diese KI ist für mich lebensähnlich.")

    cog_trust_t2_1 = make_field("Diese KI ist kompetent und effektiv bei der Vorhersage.")  # der Immobilienpreise
    cog_trust_t2_2 = make_field("Diese KI erfüllt ihre Aufgabe der Vorhersage sehr gut.")  # , die Immobilienpreise vorherzusagen,
    cog_trust_t2_3 = make_field(
        "Insgesamt ist diese KI ein fähiges und kompetentes Werkzeug für die Vorhersage.")  # der Immobilienpreise
    integ_trust_t2_1 = make_field("Diese KI gibt unvoreingenommene Empfehlungen.")
    # attention check 1
    integ_trust_t2_2 = make_field("Diese KI ist unehrlich.")
    integ_trust_t2_3 = make_field("Ich halte diese KI für integer.")
    # attention check 2
    emo_trust_t2_1 = make_field(
        "Ich fühle mich unsicher, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise
    emo_trust_t2_2 = make_field(
        "Ich fühle mich wohl, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise
    emo_trust_t2_3 = make_field(
        "Ich fühle mich zufrieden, wenn ich mich bei meiner Entscheidung auf diese KI verlasse.")  # der Immobilienpreise


# PAGES
class Intro(Page):
    form_model = 'player'
    form_fields = ['is_mobile', 'consent']


class PreQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["importance_sex", "importance_migration_bg", "importance_pol_views",
                       "age", "sex", "nationality", "migration_bg", "job_status", "immo_exp", "credit_exp",
                       "risk_aver", "pol_views", "soc_norms"]
        form_fields += player.participant.pers_inno_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # removed "sex", "migration_bg"
        demo = ["age", "nationality", "job_status", "immo_exp", "credit_exp", "risk_aver", ]
        return dict(
            demo=demo,
        )


class Task(Page):
    form_model = 'player'
    form_fields = ["task1Estimate", "conf1Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        # real estate task
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])

        # lending task
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(apartment=apartment,
                    borrower=borrower)


class PercAccuracy(Page):
    form_model = 'player'
    form_fields = ["perc_acc"]


class WTP(Page):
    form_model = "player"
    form_fields = ["wtp"]

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row1])

        return dict(developer=developer)


class Revision(Page):
    form_model = 'player'
    form_fields = ["revision", "confRevision",
                   "click_sex_open", "click_sex_close",
                   "click_migration_bg_open", "click_migration_bg_close",
                   "click_pol_views_open", "click_pol_views_close",
                   "click_acc_open", "click_acc_close"]

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row1])

        # real estate revision
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green', 'pred_price']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])
        apartment['pred_price'] = format_german_number(round((apartment['pred_price'] - 20_000) / 40_000)
                                                       * 40_000 + 20_000)

        # lending revision
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment', 'pred_']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(developer=developer,
                    original_estimate=format_german_number(player.task1Estimate),
                    apartment=apartment,
                    borrower=borrower)


class PostQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance_t1_1", "soc_distance_t1_2", "soc_distance_t1_3", "soc_distance_t1_4",
                       "soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3", "transparency_t1"]
        form_fields += player.participant.post_questions_order_t1
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row1])

        # TODO: @Johannes, das war ein Versuch die labels direkt an die Page zu spielen; da hat man dann aber wieder
        # TODO: das Problem der eingeschränkten Funktionalität in den {{ ... }} brackets
        # labels
        label_var_dic = {"anthro_t1_1": "Der Algorithmus ist für mich natürlich.",
                         "anthro_t1_2": "Der Algorithmus ist für mich menschenähnlich.",
                         "anthro_t1_3": "Der Algorithmus ist für mich lebensähnlich.",
                         "cog_trust_t1_1": f"Der Algorithmus ist kompetent und effektiv bei der Vorhersage der Immobilienpreise.",
                         "cog_trust_t1_2": f"Der Algorithmus erfüllt seine Aufgabe, die Immobilienpreise vorherzusagen, sehr gut.",
                         "cog_trust_t1_3": f"Insgesamt ist der Algorithmus ein fähiges und kompetentes Werkzeug für die Vorhersage der Immobilienpreise.",
                         "integ_trust_t1_1": "Der Algorithmus gibt unvoreingenommene Empfehlungen.",
                         "integ_trust_t1_2": "Der Algorithmus ist unehrlich.",
                         "integ_trust_t1_3": "Ich halte diesen Algorithmus für integer.",
                         "emo_trust_t1_1": f"Ich fühle mich unsicher, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.",
                         "emo_trust_t1_2": f"Ich fühle mich wohl, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.",
                         "emo_trust_t1_3": f"Ich fühle mich zufrieden, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse."}
        labels_order = [label_var_dic[var] for var in player.participant.post_questions_order_t1]

        # rank q
        ranks = ["soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3"]

        return dict(
            ranks=ranks,
            developer=developer,
            labels_order=labels_order
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
    form_fields = ["task2Estimate", "conf2Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        # real estate task
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])

        # lending task
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(apartment=apartment,
                    borrower=borrower)


class PercAccuracy2(Page):
    form_model = 'player'
    form_fields = ["perc_acc2"]


class WTP2(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.treatment == "none":
            return False
        else:
            return True

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row2])

        return dict(developer=developer)


class Revision2(Page):
    form_model = 'player'
    form_fields = ["revision2", "confRevision2",
                   "click_sex_open2", "click_sex_close2",
                   "click_migration_bg_open2", "click_migration_bg_close2",
                   "click_pol_views_open2", "click_pol_views_close2",
                   "click_acc_open2", "click_acc_close2"]

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row2])
        # real estate revision
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green', 'pred_price']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])
        apartment['pred_price'] = format_german_number(round((apartment['pred_price'] - 20_000) / 40_000)
                                                       * 40_000 + 20_000)

        # lending revision
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment', 'pred_']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(developer=developer,
                    original_estimate=format_german_number(player.task2Estimate),
                    apartment=apartment,
                    borrower=borrower)


class PostQuestions2(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance_t2_1", "soc_distance_t2_2", "soc_distance_t2_3", "soc_distance_t2_4",
                       "soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3", "transparency_t2"]
        form_fields += player.participant.post_questions_order_t2
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row2])

        # rank q
        ranks = ["soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3"]
        return dict(
            ranks=ranks,
            developer=developer
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
                 WTP2,
                 Revision2,
                 PostQuestions2,
                 End]
