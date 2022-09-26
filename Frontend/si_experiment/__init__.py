from otree.api import *
import pandas as pd
import random


doc = """"""


class C(BaseConstants):
    NAME_IN_URL = 'si_experiment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    CHOICES = ["Geschlecht", "Migrationshintergrund", "Politische Ansichten"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


# FUNCTIONS
def make_field(label):
    return models.IntegerField(
        choices=[1, 2, 3, 4, 5],
        label=label,
        widget=widgets.RadioSelectHorizontal
    )


def format_german_number(number, precision=0):
    # build format string
    format_str = '{{:,.{}f}}'.format(precision)

    # make number string
    number_str = format_str.format(number)

    # replace chars
    return number_str.replace(',', 'X').replace('.', ',').replace('X', '.')


def make_rank_field(label):
    return models.StringField(choices=C.CHOICES, label=label)


def shuffle_form_fields(fields, item=1):
    form_fields = fields
    blocksize = 3

    # remove items from list that are not blocks of 3
    items = form_fields[0:item]
    del form_fields[0:item]
    blocks = [form_fields[i:i + blocksize] for i in range(0, len(form_fields), blocksize)]
    for i in items:
        blocks.append([i])
    random.shuffle(blocks)

    for subblock in blocks:
        random.shuffle(subblock)
    form_fields = [formfield for subblock in blocks for formfield in subblock]
    return form_fields


def creating_session(subsession):
    for player in subsession.get_players():
        participant = player.participant
        # random page seq
        # True -> Stage 3 (Processing) first
        # False -> Stage 2 (Demand) first
        participant.stage_order = random.choice([True, False])
        # True -> Demand: Immo rel_task_name, Processing: Credit rel_task_name
        # False -> Demand: Credit rel_task_name, Processing: Immo rel_task_name
        participant.tasks_order = random.choice([True, False])

        # treatment and question/rel_task_name order randomization
        treatments = ["none", "dev", "acc", "both"]
        pre_questions = [
            "soc_norms", "del_grat", "pers_inno1", "pers_inno2", "pers_inno3"]
        post_questions_t1 = [
            "transparency_t1", "anthro_t1_1", "anthro_t1_2", "anthro_t1_3",
            "cog_trust_t1_1", "cog_trust_t1_2", "cog_trust_t1_3",
            "integ_trust_t1_1", "integ_trust_t1_2", "integ_trust_t1_3",
            "emo_trust_t1_1", "emo_trust_t1_2", "emo_trust_t1_3",
        ]

        pre_questions = shuffle_form_fields(pre_questions, 2)
        post_questions_t1 = shuffle_form_fields(post_questions_t1)
        post_questions_t2 = [item.replace("t1", "t2") for item in post_questions_t1]
        participant.treatment = random.choice(treatments)
        participant.pre_questions_order = pre_questions
        participant.post_questions_order_t1 = post_questions_t1
        participant.post_questions_order_t2 = post_questions_t2

        # rel_task_name payment relevance (random)
        participant.task_payment_relevance = random.randint(1, 2)

        # rel_task_name object randomization
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

        # post question rel_task_name adaption
        # if tasks_order:
        #     t1_str = "Immobilienpreise"
        #     t2_str = "Kreditausfallrisiko"
        # else:
        #     t1_str = "Kreditausfallrisiko"
        #     t2_str = "Immobilienpreise"
        # participant.t1_str = t1_str
        # participant.t2_str = t2_str

        # probability to see AI prediction
        participant.prob_ai = random.random()

class Player(BasePlayer):
    # intro data
    is_mobile = models.BooleanField()
    consent = models.BooleanField(choices=["Ich möchte an der Studie teilnehmen."],
                                  label="Durch das Ankreuzen des Kästchens erkläre ich mich mit der Teilnahme an der Studie einverstanden.")

    # Preliminary Questions
    age = models.IntegerField(label="Bitte geben Sie Ihr Alter an.", min=18, max=99)  # TODO: keine Fehlermeldung wenn unter 18 eingegeben wird
    job_status = models.IntegerField(
        choices=[[0, "Vollzeitbeschäftigung"], [1, "Teilzeitbeschäftigung"], [2, "Selbstständig"],
                 [3, "Hausfrau/mann"], [4, "Studium"], [5, "Rente"]],
        label="Wie ist Ihr derzeitiger Beschäftigungsstatus?")
    sex = models.IntegerField(choices=[[0, "Divers"], [1, "Weiblich"], [2, "Männlich"]],
                              widget=widgets.RadioSelect, label="Bitte geben Sie Ihr Geschlecht an.")

    migration_bg = models.BooleanField(choices=[[True, "Ja, ich habe einen Migrationshintergrund"],
                                                [False, "Nein, ich habe keinen Migrationshintergrund"]],
                                       widget=widgets.RadioSelect,
                                       label="Bitte geben Sie an, ob Sie einen Migrationshintergrund haben.")

    pol_views = models.IntegerField(choices=[[0, "0 (ganz links)"], [1, 1], [2, 2], [3, 3],
                                             [4, 4], [5, 5], [6, 6], [7, 7],
                                             [8, 8], [9, 9], [10, "10 (ganz rechts)"]],
                                    label="In der Politik reden die Leute oft von 'links' und 'rechts', wenn es darum geht, unterschiedliche politische Einstellungen zu kennzeichnen. "
                                          "Wenn Sie an Ihre eigenen politischen Ansichten denken: Wo würden Sie diese Ansichten einstufen?")

    importance_sex = make_field("Das Geschlecht")
    importance_migration_bg = make_field("Der Migrationshintergrund")
    importance_pol_views = make_field("Die politische Einstellung")

    #####################
    # Task 1 = Demand
    # Task 2 = Processing
    #####################
    
    # social distance var -- rel_task_name 1
    soc_distance_rank_t1_1 = make_rank_field("1. Platz")
    soc_distance_rank_t1_2 = make_rank_field("2. Platz")
    soc_distance_rank_t1_3 = make_rank_field("3. Platz")

    soc_distance_t1_1 = make_field("Der/Die Entwickler/in könnte ähnliche Ansichten haben wie ich.")
    soc_distance_t1_2 = make_field("Der/Die Entwickler/in könnte ähnliche Werte haben wie ich.")
    # soc_distance_t1_3 = make_field("Ich könnte zur gleichen Gruppe gehören wie der/die Entwickler/in.")
    soc_distance_t1_3 = make_field("Ich bin ein ähnlicher Mensch wie der/die Entwickler/in.")

    # social distance var -- rel_task_name 2
    soc_distance_rank_t2_1 = make_rank_field("1. Platz")
    soc_distance_rank_t2_2 = make_rank_field("2. Platz")
    soc_distance_rank_t2_3 = make_rank_field("3. Platz")

    soc_distance_t2_1 = make_field("Der/Die Entwickler/in könnte ähnliche Ansichten haben wie ich.")
    soc_distance_t2_2 = make_field("Der/Die Entwickler/in könnte ähnliche Werte haben wie ich.")
    # soc_distance_t2_3 = make_field("Ich könnte zur gleichen Gruppe gehören wie der/die Entwickler/in.")
    soc_distance_t2_3 = make_field("Ich bin ein ähnlicher Mensch wie der/die Entwickler/in.")

    soc_norms = make_field("Ich tue immer mein Bestes, um gesellschaftliche Normen zu befolgen.")

    # TODO: adjust wording and likert table
    del_grat = make_field("Ich glaube an 'Erst die Arbeit, dann das Vergnügen.'")
    # tech-savyness
    # pers_inno1 = make_field(
    #     "Wenn ich von einer neuen Technologie hören würde, würde ich nach Möglichkeiten suchen, damit zu experimentieren.")
    pers_inno1 = make_field(
        "Unter meinen Kolleg*innen bzw. Kommiliton*innen bin ich in der Regel die/der Erste, die/der neue Technologie ausprobiert.")
    pers_inno2 = make_field("Im Allgemeinen zögere ich neue Technologien auszuprobieren.")
    pers_inno3 = make_field("Ich experimentiere gerne mit neuen Technologien.")

    # task1
    task1Estimate = models.IntegerField()
    conf1Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # task2
    task2Estimate = models.IntegerField()
    conf2Estimate = make_field("Ich bin von meiner Schätzung überzeugt.")

    # perceived accuracy of AI -- rel_task_name 1 and 2
    perc_acc = models.FloatField()
    perc_acc2 = models.FloatField()

    # wtp -- rel_task_name 1 and 2
    wtp = models.FloatField()
    # wtp2 = models.FloatField()

    immo_exp = models.IntegerField(
        choices=[[0, "Keine Kenntnisse"], [1, "Wenige Kenntnisse"], [2, "Einige Kenntnisse"],
                 [3, "Viele Kenntnisse"]],
        label="Wie würden Sie Ihre Kenntnisse in der Bewertung von Immobilien einschätzen?")
    credit_exp = models.IntegerField(
        choices=[[0, "Keine Kenntnisse"], [1, "Wenige Kenntnisse"], [2, "Einige Kenntnisse"],
                 [3, "Viele Kenntnisse"]],
        label="Wie würden Sie Ihre Kenntnisse in der Bewertung von Kreditwürdigkeit einschätzen?")

    risk_aver = models.IntegerField(
        choices=[[0, "0 (äußerst risikoscheu)"], [1, 1], [2, 2], [3, 3],
                 [4, 4], [5, 5], [6, 6], [7, 7],
                 [8, 8], [9, 9], [10, "10 (äußerst risikofreudig)"]],
        label="Bitte geben Sie auf einer Skala von 0 bis 10 an, wie risikofreudig oder risikoscheu Sie sind,"
              " wobei 0 'äußerst risikoscheu' und 10 'äußerst risikofreudig' bedeutet.")

    # Revision 1
    revision = models.IntegerField()
    confRevision = make_field("Ich bin von meiner Schätzung überzeugt.")

    # Revision 2
    revision2 = models.IntegerField()
    confRevision2 = make_field("Ich bin von meiner Schätzung überzeugt.")

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

# def age_error_message(value):
#     if (value < 18) or (value > 99):
#         return "Bitte geben Sie ein Alter zwischen 18 und 99 Jahren an."

# PAGES
class Intro(Page):
    form_model = 'player'
    form_fields = ['is_mobile', 'consent']

class PreQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["importance_sex", "importance_migration_bg", "importance_pol_views",
                       "age", "sex", "migration_bg", "job_status", "immo_exp", "credit_exp",
                       "risk_aver", "pol_views"]
        form_fields += player.participant.pre_questions_order
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # removed "sex", "migration_bg" "nationality",
        demo = ["age",  "job_status", "immo_exp", "credit_exp", "risk_aver"]
        return dict(
            demo=demo,
        )


class Task2_1(Page):
    form_model = 'player'
    form_fields = ["task2Estimate", "conf2Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        # real estate rel_task_name
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])

        # lending rel_task_name
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(apartment=apartment,
                    borrower=borrower)

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.stage_order

class PercAccuracy2_1(Page):
    form_model = 'player'
    form_fields = ["perc_acc2"]

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row2])

        return dict(developer=developer)

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.stage_order

class Revision2_1(Page):
    form_model = 'player'
    form_fields = ["revision2", "confRevision2"]

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

        # probability to always see AI prediction
        prob = True

        return dict(developer=developer,
                    original_estimate=format_german_number(player.task2Estimate),
                    apartment=apartment,
                    borrower=borrower,
                    prob_ai=prob)

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.stage_order

class PostQuestions2_1(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = []
        if player.participant.treatment in ["dev", "both"]:
            form_fields = ["soc_distance_t2_1", "soc_distance_t2_2", "soc_distance_t2_3",  # "soc_distance_t2_4",
                           "soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3"]
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

    @staticmethod
    def error_message(player: Player, values):
        if player.participant.treatment in ["dev", "both"]:
            choices = [values['soc_distance_rank_t2_1'], values['soc_distance_rank_t2_2'], values['soc_distance_rank_t2_3']]
            # set() gives you distinct elements. if a list's length is different from its
            # set length, that means it must have duplicates.
            if len(set(choices)) != len(choices):
                return "Sie können nicht dasselbe Element mehrfach auswählen."

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.stage_order

class Stage2_1(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.stage_order

class Task(Page):
    form_model = 'player'
    form_fields = ["task1Estimate", "conf1Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        # real estate rel_task_name
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])

        # lending rel_task_name
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

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row1])

        return dict(developer=developer)


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
    form_fields = ["revision", "confRevision"]

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

        # probability to see AI prediction
        prob = player.participant.prob_ai <= player.wtp/100
        player.participant.ai = prob

        return dict(developer=developer,
                    original_estimate=format_german_number(player.task1Estimate),
                    apartment=apartment,
                    borrower=borrower,
                    prob_ai=prob)


class PostQuestions(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = []
        if player.participant.treatment in ["dev", "both"]:
            form_fields = ["soc_distance_t1_1", "soc_distance_t1_2", "soc_distance_t1_3", # "soc_distance_t1_4",
                           "soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3"]
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
        # label_var_dic = {"anthro_t1_1": "Der Algorithmus ist für mich natürlich.",
        #                  "anthro_t1_2": "Der Algorithmus ist für mich menschenähnlich.",
        #                  "anthro_t1_3": "Der Algorithmus ist für mich lebensähnlich.",
        #                  "cog_trust_t1_1": f"Der Algorithmus ist kompetent und effektiv bei der Vorhersage der Immobilienpreise.",
        #                  "cog_trust_t1_2": f"Der Algorithmus erfüllt seine Aufgabe, die Immobilienpreise vorherzusagen, sehr gut.",
        #                  "cog_trust_t1_3": f"Insgesamt ist der Algorithmus ein fähiges und kompetentes Werkzeug für die Vorhersage der Immobilienpreise.",
        #                  "integ_trust_t1_1": "Der Algorithmus gibt unvoreingenommene Empfehlungen.",
        #                  "integ_trust_t1_2": "Der Algorithmus ist unehrlich.",
        #                  "integ_trust_t1_3": "Ich halte diesen Algorithmus für integer.",
        #                  "emo_trust_t1_1": f"Ich fühle mich unsicher, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.",
        #                  "emo_trust_t1_2": f"Ich fühle mich wohl, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse.",
        #                  "emo_trust_t1_3": f"Ich fühle mich zufrieden, wenn ich mich bei meiner Entscheidung der Immobilienpreise auf diesen Algorithmus verlasse."}
        # labels_order = [label_var_dic[var] for var in player.participant.post_questions_order_t1]

        # rank q
        ranks = ["soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3"]

        return dict(
            ranks=ranks,
            developer=developer,
            # labels_order=labels_order
        )

    @staticmethod
    def error_message(player: Player, values):
        if player.participant.treatment in ["dev", "both"]:
            choices = [values['soc_distance_rank_t1_1'], values['soc_distance_rank_t1_2'], values['soc_distance_rank_t1_3']]
            # set() gives you distinct elements. if a list's length is different from its
            # set length, that means it must have duplicates.
            if len(set(choices)) != len(choices):
                return "Sie können nicht dasselbe Element mehrfach auswählen."


class Stage2(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.stage_order

class Task2(Page):
    form_model = 'player'
    form_fields = ["task2Estimate", "conf2Estimate"]

    @staticmethod
    def vars_for_template(player: Player):
        # real estate rel_task_name
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = apartments[['garden', 'basement', 'elevator', 'balcony',
                                 'floor', 'n_rooms', 'sq_meters', 'construction_year',
                                 'unemployment', 'share_green']]
        apartment = dict(apartments.iloc[player.participant.apartment_row])

        # lending rel_task_name
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        for col in ['loan_amnt', 'annual_inc', 'installment']:
            borrowers[col] = [format_german_number(x, 0) for x in borrowers[col]]
        for col in ['open_acc', 'emp_length', 'term']:
            borrowers[col] = borrowers[col].astype(int)
        borrower = dict(borrowers.iloc[player.participant.lender_row])

        return dict(apartment=apartment,
                    borrower=borrower)

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.stage_order

class PercAccuracy2(Page):
    form_model = 'player'
    form_fields = ["perc_acc2"]

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row2])

        return dict(developer=developer)

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.stage_order

class Revision2(Page):
    form_model = 'player'
    form_fields = ["revision2", "confRevision2"]

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

        # probability to always see AI prediction
        prob = True

        return dict(developer=developer,
                    original_estimate=format_german_number(player.task2Estimate),
                    apartment=apartment,
                    borrower=borrower,
                    prob_ai=prob)

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.stage_order

class PostQuestions2(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = []
        if player.participant.treatment in ["dev", "both"]:
            form_fields = ["soc_distance_t2_1", "soc_distance_t2_2", "soc_distance_t2_3",  # "soc_distance_t2_4",
                           "soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3"]
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

    @staticmethod
    def error_message(player: Player, values):
        if player.participant.treatment in ["dev", "both"]:
            choices = [values['soc_distance_rank_t2_1'], values['soc_distance_rank_t2_2'], values['soc_distance_rank_t2_3']]
            # set() gives you distinct elements. if a list's length is different from its
            # set length, that means it must have duplicates.
            if len(set(choices)) != len(choices):
                return "Sie können nicht dasselbe Element mehrfach auswählen."

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.stage_order

class SocDist2_1(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance_t2_1", "soc_distance_t2_2", "soc_distance_t2_3",  # "soc_distance_t2_4",
                       "soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3"]
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

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.treatment in ["none", "acc"] and player.participant.stage_order:
            return True
        else:
            return False

class SocDist1(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance_t1_1", "soc_distance_t1_2", "soc_distance_t1_3",  #"soc_distance_t1_4",
                       "soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3"]
        return form_fields

    @staticmethod
    def vars_for_template(player: Player):
        # developer
        developers = pd.read_csv("Data/dev_profiles.csv")
        developer = dict(developers.iloc[player.participant.dev_row1])

        # rank q
        ranks = ["soc_distance_rank_t1_1", "soc_distance_rank_t1_2", "soc_distance_rank_t1_3"]
        return dict(
            ranks=ranks,
            developer=developer
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.treatment in ["none", "acc"]:
            return True
        else:
            return False

    @staticmethod
    def error_message(player: Player, values):
        choices = [values['soc_distance_rank_t1_1'], values['soc_distance_rank_t1_2'], values['soc_distance_rank_t1_3']]
        # set() gives you distinct elements. if a list's length is different from its
        # set length, that means it must have duplicates.
        if len(set(choices)) != len(choices):
            return "Sie können nicht dasselbe Element mehrfach auswählen."

class SocDist2(Page):
    form_model = "player"

    @staticmethod
    def get_form_fields(player: Player):
        form_fields = ["soc_distance_t2_1", "soc_distance_t2_2", "soc_distance_t2_3",  # "soc_distance_t2_4",
                       "soc_distance_rank_t2_1", "soc_distance_rank_t2_2", "soc_distance_rank_t2_3"]
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

    @staticmethod
    def is_displayed(player: Player):
        if player.participant.treatment in ["none", "acc"] and not player.participant.stage_order:
            return True
        else:
            return False

    @staticmethod
    def error_message(player: Player, values):
        choices = [values['soc_distance_rank_t2_1'], values['soc_distance_rank_t2_2'], values['soc_distance_rank_t2_3']]
        # set() gives you distinct elements. if a list's length is different from its
        # set length, that means it must have duplicates.
        if len(set(choices)) != len(choices):
            return "Sie können nicht dasselbe Element mehrfach auswählen."

class End(Page):
    def vars_for_template(player: Player):
        # real estate rel_task_name
        apartments = pd.read_csv("Data/immonet_data_selected.csv")
        apartments = round((apartments['price'] - 300_000) / 40_000)*40_000 + 300_000
        apartment = int(apartments.iloc[player.participant.apartment_row])

        # lending rel_task_name
        borrowers = pd.read_csv("Data/lending_data_selected.csv")
        borrowers = borrowers['y_']
        borrower = int(borrowers.iloc[player.participant.lender_row])

        fail_str, succ_str = "Sie lagen leider daneben.", "Sie haben richtig geschätzt!"
        apartment_res, borrower_res = fail_str, fail_str
        if player.participant.tasks_order:
            # TODO: rel_task_name estimate -> Revision
            t1_correct = player.revision == apartment
            apart_est, apart_correct = format_german_number(player.revision), format_german_number(apartment)

            t2_correct = player.revision2 == borrower

            if t1_correct:
                apartment_res = succ_str
            if t2_correct:
                borrower_res = succ_str
        else:
            t1_correct = player.revision == borrower

            t2_correct = player.revision2 == apartment
            apart_est, apart_correct = format_german_number(player.revision2), format_german_number(apartment)

            if t1_correct:
                borrower_res = succ_str
            if t2_correct:
                apartment_res = succ_str

        if player.participant.stage_order and player.participant.task_payment_relevance == 1:
            task_str = player.participant.task_payment_relevance + 1
        elif player.participant.stage_order and player.participant.task_payment_relevance == 2:
            task_str = player.participant.task_payment_relevance - 1
        else:
            task_str = player.participant.task_payment_relevance

        feedback_str = f"Aufgabe {task_str} ist relevant für Ihre Auszahlung. "
        if (player.participant.task_payment_relevance == 1 and t1_correct) or (player.participant.task_payment_relevance == 2 and t2_correct):
            feedback_str = feedback_str + f"Herzlichen Glückwunsch, <b>Ihre variable Vergütung beträgt somit insgesamt " \
                                          f"{format_german_number(0.01*(30 - abs(player.wtp - 50)) + 5, 2)} EUR.</b> <br>" \
                                          f"({format_german_number(5, 2)} für die Schätzung und " \
                                          f"{format_german_number(0.01*(30 - abs(player.wtp - 50)), 2)} Restbudget)."
            player.participant.var_payment_amount = 0.01*(30 - abs(player.wtp - 50)) + 5
        else:
            feedback_str = feedback_str + f"Ihre <b>variable Vergütung beträgt somit insgesamt " \
                                          f"{format_german_number(0.01*(30 - abs(player.wtp - 50)), 2)} EUR.</b> <br>" \
                                          f"({format_german_number(0, 2)} EUR für die Schätzung und " \
                                          f"{format_german_number(0.01*(30 - abs(player.wtp - 50)), 2)} EUR Restbudget)."
            player.participant.var_payment_amount = 0.01 * (30 - abs(player.wtp - 50))


        return dict(apartment=apartment,
                    borrower=borrower,
                    apartment_res=apartment_res,
                    apart_est=apart_est,
                    apart_correct=apart_correct,
                    borrower_res=borrower_res,
                    feedback_str=feedback_str
                    )


page_sequence = [Intro,
                 PreQuestions,
                 Task2_1,
                 PercAccuracy2_1,
                 Revision2_1,
                 PostQuestions2_1,
                 Stage2_1,
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
                 SocDist2_1,
                 SocDist1,
                 SocDist2,
                 End]
