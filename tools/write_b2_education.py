#!/usr/bin/env python3
"""
Hand-written replacement for the four B2 Education passages (B2_241-B2_244).

Unlike regenerate_b2_passages.py, nothing here is produced from a shared
sentence skeleton. Each passage is a separate piece of prose about a different
named centre, written to the standard set by WRITING_GUIDE.md and by the
hand-written B2_321.

This script rewrites, for each of the four files:
  - passage.sections (headings and text)
  - passage.full_text
  - questions (all 25)
  - answer_key (mirrored from questions)

Everything else - cefr, topic, metadata, timings - is preserved.

Question anchors are verbatim substrings of the paragraph they point at, because
js/app.js highlights them with a literal string split. The script asserts this.

All people, organisations and figures are synthetic practice material; the
cities are real.
"""

import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "B2")

FILES = {
    "B2-241": "B2_241_education_origins_and_daily_operation_in_community_learning_centres.json",
    "B2-242": "B2_242_education_benefits_and_unexpected_costs_in_community_learning_centres.json",
    "B2-243": "B2_243_education_measurement_and_evidence_in_community_learning_centres.json",
    "B2-244": "B2_244_education_future_choices_and_governance_in_community_learning_centres.json",
}


# --------------------------------------------------------------------------
# B2-241 - Brookfield Learning Room, Leicester: origins and daily operation
# --------------------------------------------------------------------------

P241 = [
    ("A shop unit in Leicester",
     "When the last adult education college in the east of Leicester closed in 2010, Margaret Ellis was "
     "six months into her retirement after thirty-one years teaching secondary English. She began by "
     "tutoring two neighbours at her kitchen table. By March 2011 there were eleven learners, and a "
     "butcher on Green Lane Road lent her the empty shop unit above his cold store on Tuesday and "
     "Thursday evenings. That arrangement gave the project its name: the Brookfield Learning Room. Ellis "
     "registered it as a charity in 2013, mainly so that it could hold a bank account in its own name. "
     "Fourteen years later it teaches around 480 adults a year across three sites, and it still has no "
     "permanent building of its own."),

    ("What a week looks like",
     "Brookfield does not run terms. Learners enrol in any week of the year and attend when their shifts "
     "allow, which is why the timetable repeats the same three courses — basic literacy, numeracy, and "
     "using online public services — on four evenings and on Saturday mornings. A typical Tuesday brings "
     "between fourteen and twenty people to the Green Lane site. Two paid tutors work alongside five or "
     "six volunteers, most of them former learners. Nobody is turned away for arriving late. The centre "
     "does keep a register, but its main purpose is not to check up on anyone. It tells tutors who has "
     "not been seen for a fortnight, so that somebody can telephone them before the gap becomes "
     "permanent."),

    ("Paying for it",
     "The three sites cost about £210,000 a year to run, of which roughly two-thirds goes on wages "
     "for four part-time staff. Around £60,000 comes from Leicester City Council, £85,000 "
     "from a national adult-skills fund, and the remainder from room hire, a small second-hand bookshop, "
     "and donations. Almost all of it is agreed twelve months at a time. Ellis, who now chairs the "
     "trustees rather than teaching, describes the consequences plainly: the charity cannot sign a lease "
     "longer than a year, cannot offer a tutor a permanent contract, and spends about seven weeks of "
     "every year writing funding applications. Two of the three sites are in borrowed rooms for exactly "
     "this reason."),

    ("Where the model strains",
     "The openness that makes Brookfield work also undermines it. Roughly a third of those who enrol stop "
     "attending before their course ends, and the drop-out rate is highest among the learners who arrived "
     "with the weakest skills. Tutors say the reasons are rarely to do with the teaching: a change of "
     "shift pattern, a child's illness, a move to another part of the city. Because there are no fixed "
     "terms, there is also no moment at which a missing learner is formally noticed. The register catches "
     "most of them. But a volunteer making telephone calls in her own time is a fragile substitute for "
     "the pastoral system a college would have employed someone to run."),

    ("Decisions ahead",
     "In 2024 the trustees were asked to consider charging for a new set of short courses in bookkeeping "
     "and spreadsheet skills, aimed at people already in work. The fees would be modest, perhaps £45 "
     "for six weeks, but they would be reliable in a way that grants are not. Three trustees "
     "argued that any charge at all would deter exactly the people the charity exists to serve. Others "
     "pointed out that a paid course could quietly subsidise the free ones. The decision was deferred to "
     "2026. Ellis, now 78, is more troubled by a different question: nobody has yet been identified to "
     "replace her, and most of what the charity knows about its learners is not written down anywhere."),
]

Q241 = [
    ("multiple_choice", "detail", 1,
     "the last adult education college in the east of Leicester closed in 2010",
     "What prompted Margaret Ellis to begin tutoring?",
     ["She was asked to do so by Leicester City Council.",
      "The last adult education college in the east of the city had closed.",
      "She wanted to earn extra income after retiring.",
      "A local butcher offered her the use of an empty shop unit."],
     "B",
     "Paragraph 1 opens by linking Ellis's first tutoring to the closure of the last adult education "
     "college in east Leicester in 2010. The shop unit in option D came later, in 2011, and was a "
     "consequence of the project rather than its cause."),

    ("true_false_not_given", "detail", 1,
     "a butcher on Green Lane Road lent her the empty shop unit above his cold store",
     "Brookfield Learning Room owns the building in which it was first based.",
     None, "FALSE",
     "The first premises were lent by a butcher, and the paragraph ends by stating that the centre "
     "still has no permanent building of its own. The statement contradicts the text."),

    ("matching_information", "reference", 3,
     "cannot offer a tutor a permanent contract",
     "Which paragraph explains why the centre cannot offer its tutors permanent contracts?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 3",
     "Paragraph 3 links the twelve-month funding cycle to three specific consequences, one of which "
     "is that no tutor can be given a permanent contract."),

    ("sentence_completion", "detail", 2,
     "most of them former learners",
     "Complete the sentence: Most of the volunteers who work alongside the paid tutors are ____.",
     None, "former learners",
     "Paragraph 2 states that the five or six volunteers are 'most of them former learners'.",
     "NO MORE THAN TWO WORDS"),

    ("short_answer", "detail", 1,
     "Ellis registered it as a charity in 2013",
     "In which year was the project registered as a charity?",
     None, "2013",
     "Paragraph 1 states that Ellis registered the project as a charity in 2013 so that it could hold "
     "a bank account in its own name.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 3,
     "cannot sign a lease longer than a year",
     "Why are two of the centre's three sites in borrowed rooms?",
     ["The rooms are provided free of charge by Leicester City Council.",
      "Its funding is confirmed only a year at a time, so it cannot commit to a longer lease.",
      "Learners prefer venues that are close to their own homes.",
      "The charity spends its whole income on wages for part-time staff."],
     "B",
     "Paragraph 3 explains that almost all funding is agreed twelve months at a time, so the charity "
     "cannot sign a lease longer than a year, and says that the borrowed rooms exist 'for exactly this "
     "reason'. Wages account for two-thirds of spending, not all of it, so D overstates the text."),

    ("true_false_not_given", "inference", 2,
     "Two paid tutors work alongside five or six volunteers",
     "The centre's volunteers receive formal training before they begin tutoring.",
     None, "NOT GIVEN",
     "Paragraph 2 says how many volunteers there are and where most of them come from, but says "
     "nothing at all about training. The passage neither confirms nor contradicts the statement."),

    ("matching_information", "reference", 4,
     "the drop-out rate is highest among the learners who arrived with the weakest skills",
     "Which paragraph identifies the learners most likely to stop attending?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 4",
     "Paragraph 4 states that drop-out is highest among those who arrived with the weakest skills."),

    ("sentence_completion", "detail", 5,
     "The decision was deferred to 2026",
     "Complete the sentence: The trustees postponed their decision on charging fees until ____.",
     None, "2026",
     "Paragraph 5 records that the decision on paid short courses was deferred to 2026.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 3,
     "Around £60,000 comes from Leicester City Council",
     "Which body provides around £60,000 of the centre's annual income?",
     None, "Leicester City Council",
     "Paragraph 3 attributes around £60,000 of the annual budget to Leicester City Council.",
     "NO MORE THAN THREE WORDS"),

    ("multiple_choice", "writer_purpose", 4,
     "a volunteer making telephone calls in her own time is a fragile substitute",
     "Why does the writer mention 'a volunteer making telephone calls in her own time'?",
     ["To praise the dedication shown by the centre's volunteers.",
      "To show that the centre's follow-up depends on something too informal to be dependable.",
      "To explain why the centre decided to keep a register at all.",
      "To argue that colleges should employ more pastoral staff."],
     "B",
     "The phrase appears inside a comparison: the volunteer's calls are 'a fragile substitute' for a "
     "system a college would have paid someone to run. The point is the weakness of the arrangement, "
     "not the merit of the volunteer."),

    ("true_false_not_given", "detail", 5,
     "nobody has yet been identified to replace her",
     "Ellis has already chosen someone to succeed her.",
     None, "FALSE",
     "Paragraph 5 states directly that nobody has yet been identified to replace her."),

    ("matching_information", "reference", 2,
     "basic literacy, numeracy, and using online public services",
     "Which paragraph lists the subjects taught at the centre?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 2",
     "Paragraph 2 names the three repeated courses: basic literacy, numeracy, and using online public "
     "services."),

    ("sentence_completion", "detail", 4,
     "the reasons are rarely to do with the teaching",
     "Complete the sentence: Tutors report that learners usually leave for reasons that have little to "
     "do with the ____.",
     None, "teaching",
     "Paragraph 4 reports tutors as saying the reasons are rarely to do with the teaching, and then "
     "lists shift changes, illness and moving house.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "It tells tutors who has not been seen for a fortnight",
     "How long is a learner absent before the register prompts a tutor to make contact?",
     None, "a fortnight",
     "Paragraph 2 explains that the register's purpose is to tell tutors who has not been seen for a "
     "fortnight.",
     "NO MORE THAN TWO WORDS"),

    ("multiple_choice", "main_idea", 1,
     "Fourteen years later it teaches around 480 adults a year across three sites",
     "Which statement best summarises the centre's development since 2011?",
     ["It expanded steadily once it had secured a permanent building of its own.",
      "It grew from eleven learners in a borrowed shop to around 480 a year, still without premises "
      "of its own.",
      "It was taken over by Leicester City Council and expanded to three sites.",
      "It has stayed roughly the same size since it was registered as a charity."],
     "B",
     "Paragraph 1 traces the growth from eleven learners in 2011 to around 480 adults a year across "
     "three sites, and closes by noting that it still has no permanent building."),

    ("true_false_not_given", "detail", 3,
     "roughly two-thirds goes on wages",
     "Most of the centre's annual budget is spent on staff wages.",
     None, "TRUE",
     "Paragraph 3 states that roughly two-thirds of the £210,000 goes on wages for four "
     "part-time staff, which is a majority of the budget."),

    ("matching_information", "reference", 5,
     "Three trustees argued that any charge at all would deter",
     "Which paragraph reports a disagreement among the trustees?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 5",
     "Paragraph 5 sets out the split between three trustees opposed to any charge and others who saw "
     "fees as a way of subsidising free courses."),

    ("sentence_completion", "detail", 1,
     "tutoring two neighbours at her kitchen table",
     "Complete the sentence: Ellis began by tutoring two ____ at her kitchen table.",
     None, "neighbours",
     "Paragraph 1 states that she began by tutoring two neighbours at her kitchen table.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "on four evenings and on Saturday mornings",
     "On which day of the week does the centre run morning sessions?",
     None, "Saturday",
     "Paragraph 2 states that the timetable runs on four evenings and on Saturday mornings.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 5,
     "most of what the charity knows about its learners is not written down anywhere",
     "What worries Ellis most about the centre's future?",
     ["That fees would deter the learners the charity was set up to serve.",
      "That the national adult-skills fund will be withdrawn.",
      "That the centre depends on knowledge held by individuals and recorded nowhere.",
      "That the three sites are too far apart to be managed properly."],
     "C",
     "Paragraph 5 contrasts the fees debate with what troubles Ellis more: no successor has been "
     "identified, and the charity's knowledge of its learners is unrecorded. Option A is the argument "
     "made by three other trustees, not Ellis's own concern."),

    ("true_false_not_given", "detail", 5,
     "aimed at people already in work",
     "The proposed short courses are intended for people who already have jobs.",
     None, "TRUE",
     "Paragraph 5 describes the bookkeeping and spreadsheet courses as aimed at people already in "
     "work."),

    ("matching_information", "reference", 1,
     "That arrangement gave the project its name",
     "Which paragraph explains how the centre acquired its name?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 1",
     "Paragraph 1 states that the arrangement with the butcher gave the project its name, the "
     "Brookfield Learning Room."),

    ("sentence_completion", "detail", 3,
     "who now chairs the trustees rather than teaching",
     "Complete the sentence: Ellis now chairs the ____ rather than teaching.",
     None, "trustees",
     "Paragraph 3 describes Ellis as someone who now chairs the trustees rather than teaching.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 1,
     "tutoring two neighbours at her kitchen table",
     "Where did Ellis teach her first two learners?",
     None, "her kitchen table",
     "Paragraph 1 states that she began by tutoring two neighbours at her kitchen table.",
     "NO MORE THAN THREE WORDS"),
]


# --------------------------------------------------------------------------
# B2-242 - Shandon Skills Room, Cork: benefits and unexpected costs
# --------------------------------------------------------------------------

P242 = [
    ("A success by its own measure",
     "The Shandon Skills Room opened in a former parish hall in the north of Cork in 2013 with one "
     "stated aim: to bring adults who had left school early back into formal qualifications. On that "
     "measure it has done well. Between 2013 and 2024 it entered more than thirteen hundred adults for "
     "state examinations, and 71% of them passed at least one subject. Nuala Doyle, who founded the "
     "centre after twenty years managing a credit union, keeps the pass figures on a whiteboard beside "
     "the front door. They are the first thing funders are shown. They are also the reason the "
     "Department of Education renewed the centre's grant in 2022 without asking for a formal review."),

    ("What the certificate did not cover",
     "The qualifications did not always lead where learners expected. A follow-up study by University "
     "College Cork in 2023 traced 200 former students two years after they had passed. Just under half "
     "had moved into better-paid work or further study. The rest had not, and several of them said the "
     "certificate had cost them something: fees for the examinations, evenings away from their children, "
     "and in eleven cases the loss of a means-tested payment once their circumstances were reassessed. "
     "Doyle accepts the finding. 'We were selling a qualification,' she said, 'and some people bought a "
     "qualification and nothing else.' The centre now runs a short session on benefits before enrolment."),

    ("The volunteers who stopped volunteering",
     "A second cost fell on the people who ran the place. Of the nineteen volunteer tutors active in "
     "2016, only four were still tutoring by 2023. Most left quietly, and the centre did not record its "
     "conversations with departing volunteers until 2021. Those it does have point to the same pressure. "
     "As examination entries rose, tutoring became less like a conversation and more like preparation "
     "for a paper, with marking to be taken home. Two former volunteers said they had joined to help "
     "neighbours read and had ended up as unpaid examiners. Recruitment has grown harder every year, and "
     "since 2022 the centre has paid three tutors it would once have expected to find for nothing."),

    ("Counting the wrong thing",
     "The pass rate on Doyle's whiteboard is accurate, but it describes only those who sat the "
     "examination. Learners who withdrew before the entry deadline are not counted at all, and they are "
     "roughly a quarter of everyone who enrols. Counted the other way - passes as a share of all "
     "enrolments rather than of all candidates — the figure falls from 71% to about 53%. Neither number "
     "is wrong. They answer different questions, and the centre has consistently published the more "
     "flattering one. That mattered little while the grant was secure. It matters more now that a "
     "neighbouring county has begun citing Cork's figures in support of a centre of its own."),

    ("An honest prospectus",
     "Doyle has argued since 2023 for printing both figures in the annual report, together with the "
     "University College Cork follow-up. Two trustees disagree. Their case is not that the fuller "
     "account is untrue but that it is complicated, and that a complicated account is harder to defend "
     "at a funding meeting than a single strong number. The compromise reached in 2024 was to print both "
     "rates but to place the follow-up study in an appendix. Whether that satisfies anyone is unclear. "
     "What the argument has produced, at least, is a centre that now knows the difference between the "
     "questions it answers well and the questions it has never really asked."),
]

Q242 = [
    ("multiple_choice", "main_idea", 1,
     "to bring adults who had left school early back into formal qualifications",
     "What was the Shandon Skills Room originally set up to do?",
     ["Provide free childcare for parents attending evening classes.",
      "Help adults who had left school early to gain formal qualifications.",
      "Train local volunteers to work as state examiners.",
      "Replace a parish hall that had closed in the north of Cork."],
     "B",
     "Paragraph 1 gives the centre's single stated aim: bringing adults who had left school early back "
     "into formal qualifications."),

    ("true_false_not_given", "detail", 1,
     "renewed the centre's grant in 2022 without asking for a formal review",
     "The Department of Education carried out a formal review before renewing the grant in 2022.",
     None, "FALSE",
     "Paragraph 1 states that the grant was renewed in 2022 without a formal review being requested."),

    ("matching_information", "reference", 4,
     "They answer different questions",
     "Which paragraph explains how two different pass rates can both be accurate?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 4",
     "Paragraph 4 sets the 71% figure against the 53% figure and states that neither is wrong because "
     "they answer different questions."),

    ("sentence_completion", "detail", 3,
     "only four were still tutoring by 2023",
     "Complete the sentence: Of the nineteen volunteer tutors active in 2016, only ____ were still "
     "tutoring by 2023.",
     None, "four",
     "Paragraph 3 records that four of the nineteen volunteers active in 2016 were still tutoring in "
     "2023.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 1,
     "71% of them passed at least one subject",
     "What percentage of those entered for examinations passed at least one subject?",
     None, "71%",
     "Paragraph 1 states that 71% of the adults entered passed at least one subject.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "detail", 2,
     "Just under half had moved into better-paid work or further study",
     "What did the University College Cork study find about the former students it traced?",
     ["All of them had found better-paid work within two years.",
      "Slightly fewer than half had moved into better work or further study.",
      "Most had returned to the centre for a second qualification.",
      "The majority had lost a means-tested payment."],
     "B",
     "Paragraph 2 reports that just under half had moved into better-paid work or further study. The "
     "loss of a means-tested payment affected eleven of the 200, not a majority."),

    ("true_false_not_given", "detail", 2,
     "The centre now runs a short session on benefits before enrolment",
     "The centre now warns learners about possible effects on their benefits before they enrol.",
     None, "TRUE",
     "Paragraph 2 ends by stating that a short session on benefits is now held before enrolment, in "
     "response to the eleven cases of lost payments."),

    ("matching_information", "reference", 3,
     "the centre has paid three tutors it would once have expected to find for nothing",
     "Which paragraph explains why the centre began paying people it had previously not paid?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 3",
     "Paragraph 3 links the loss of volunteers and the difficulty of recruitment to the decision, from "
     "2022, to pay three tutors."),

    ("sentence_completion", "detail", 2,
     "the loss of a means-tested payment once their circumstances were reassessed",
     "Complete the sentence: Eleven former students lost a ____ payment once their circumstances were "
     "reassessed.",
     None, "means-tested",
     "Paragraph 2 lists the loss of a means-tested payment in eleven cases among the costs of gaining "
     "the certificate.",
     "NO MORE THAN TWO WORDS"),

    ("short_answer", "writer_purpose", 4,
     "the centre has consistently published the more flattering one",
     "Which single word does the writer use to describe the pass rate the centre chooses to publish?",
     None, "flattering",
     "Paragraph 4 says the centre has consistently published the more flattering of the two accurate "
     "figures.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "writer_purpose", 3,
     "had ended up as unpaid examiners",
     "Why does the writer mention the volunteers who 'ended up as unpaid examiners'?",
     ["To show that the volunteers had been poorly trained.",
      "To illustrate how the focus on examinations changed the work volunteers had signed up for.",
      "To explain why the number of examination entries rose.",
      "To criticise the state examination system."],
     "B",
     "The remark sits inside an explanation of why volunteers left: tutoring turned into examination "
     "preparation and marking, which was not the work they had volunteered for."),

    ("true_false_not_given", "detail", 3,
     "the centre did not record its conversations with departing volunteers until 2021",
     "The centre recorded its conversations with departing volunteers from the beginning.",
     None, "FALSE",
     "Paragraph 3 states that such conversations were not recorded until 2021, well after the centre "
     "opened in 2013."),

    ("matching_information", "reference", 5,
     "The compromise reached in 2024",
     "Which paragraph reports a compromise reached in 2024?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 5",
     "Paragraph 5 describes the 2024 compromise: both rates printed, but the follow-up study placed in "
     "an appendix."),

    ("sentence_completion", "detail", 4,
     "the figure falls from 71% to about 53%",
     "Complete the sentence: Measured against all enrolments rather than all candidates, the pass rate "
     "falls to about ____.",
     None, "53%",
     "Paragraph 4 gives about 53% as the pass rate when calculated as a share of all enrolments.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 5,
     "to place the follow-up study in an appendix",
     "In which part of the annual report was the follow-up study placed?",
     None, "appendix",
     "Paragraph 5 states that the 2024 compromise placed the follow-up study in an appendix.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "main_idea", 4,
     "it describes only those who sat the examination",
     "What is the writer's main point in the fourth paragraph?",
     ["The centre has published figures it knew to be false.",
      "The centre's headline figure is accurate but answers a narrower question than readers assume.",
      "Learners who withdraw should be entered for examinations anyway.",
      "A neighbouring county has deliberately misused the centre's data."],
     "B",
     "The paragraph insists that neither number is wrong; the difficulty is that the published figure "
     "covers only candidates, while readers are likely to take it as covering everyone who enrolled."),

    ("true_false_not_given", "inference", 4,
     "a neighbouring county has begun citing Cork's figures in support of a centre of its own",
     "The neighbouring county has been refused permission to open its own centre.",
     None, "NOT GIVEN",
     "Paragraph 4 says only that the county is citing Cork's figures in support of a centre. Nothing "
     "is said about whether permission was sought or refused."),

    ("matching_information", "reference", 2,
     "fees for the examinations, evenings away from their children",
     "Which paragraph gives examples of a qualification bringing unexpected costs?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 2",
     "Paragraph 2 lists examination fees, lost evenings with children, and lost means-tested payments."),

    ("sentence_completion", "detail", 1,
     "opened in a former parish hall in the north of Cork in 2013",
     "Complete the sentence: The centre opened in 2013 in a former ____ in the north of Cork.",
     None, "parish hall",
     "Paragraph 1 identifies the premises as a former parish hall.",
     "NO MORE THAN TWO WORDS"),

    ("short_answer", "detail", 3,
     "since 2022 the centre has paid three tutors",
     "From which year has the centre paid tutors it once expected to find for nothing?",
     None, "2022",
     "Paragraph 3 states that the centre has paid three such tutors since 2022.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 5,
     "harder to defend at a funding meeting than a single strong number",
     "Why do two trustees oppose publishing the fuller account?",
     ["They believe the follow-up study is inaccurate.",
      "They think a complicated account is harder to defend when seeking funding.",
      "They want to protect the privacy of former students.",
      "They disagree with Doyle about the centre's aims."],
     "B",
     "Paragraph 5 is explicit that their objection is not that the fuller account is untrue, but that "
     "its complexity makes it harder to defend at a funding meeting."),

    ("true_false_not_given", "detail", 5,
     "Doyle has argued since 2023 for printing both figures in the annual report",
     "Doyle wants both pass rates to appear in the centre's annual report.",
     None, "TRUE",
     "Paragraph 5 states that Doyle has argued since 2023 for printing both figures in the annual "
     "report."),

    ("matching_information", "reference", 1,
     "after twenty years managing a credit union",
     "Which paragraph describes what Doyle did before founding the centre?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 1",
     "Paragraph 1 states that Doyle founded the centre after twenty years managing a credit union."),

    ("sentence_completion", "detail", 3,
     "with marking to be taken home",
     "Complete the sentence: As examination entries rose, tutoring came to involve ____ that had to be "
     "taken home.",
     None, "marking",
     "Paragraph 3 describes tutoring becoming preparation for a paper, with marking to be taken home.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "traced 200 former students two years after they had passed",
     "How many years after passing were the former students traced?",
     None, "two",
     "Paragraph 2 states that the study traced 200 former students two years after they had passed.",
     "NO MORE THAN ONE WORD"),
]


# --------------------------------------------------------------------------
# B2-243 - Iltatupa network, Tampere: measurement and evidence
# --------------------------------------------------------------------------

P243 = [
    ("Records that were never meant to be data",
     "When the city library service in Tampere opened its first Iltatupa, or 'evening room', in 2015, "
     "nobody expected the service to be evaluated. The rooms were a small addition to libraries that "
     "already existed: a table, a tutor for three hours on weekday evenings, and free help with Finnish, "
     "job applications, and government websites. Staff logged each visit on a paper sheet because the "
     "caretaker needed to know when the building could be locked. Nine years and eleven rooms later, "
     "those sheets are the only continuous record of who has used the service. They were designed for a "
     "purpose that had nothing whatever to do with measuring anything."),

    ("What the tally cannot see",
     "The paper sheets record a date, a room, and a tally. They do not record names, so a person who "
     "visits forty times appears in the totals as forty separate visits. In 2022 the service reported "
     "more than thirty-eight thousand visits and was congratulated on reaching a large number of "
     "residents. Dr Hanna Virtanen of Tampere University, asked to review the figures, pointed out that "
     "the reported total was equally consistent with thirty-eight thousand people attending once and "
     "with a thousand people attending thirty-eight times each. Those two services would need entirely "
     "different staffing. The tally could not tell them apart, and nobody had noticed the ambiguity for "
     "seven years."),

    ("A stronger test",
     "Virtanen's team ran a small study in 2023 to settle the question. For six weeks, tutors in four "
     "rooms asked every visitor one thing as they arrived: had they been before? The answers suggested "
     "that about 62% of visits were made by people who had already attended at least five times. The "
     "service was therefore doing something its totals had never shown — supporting a small core group "
     "intensively — rather than what it had assumed it was doing. The study was cheap, because it used "
     "tutors who were on duty anyway, and it changed the way the service described itself in the next "
     "funding application it wrote."),

    ("Where the evidence runs out",
     "What the study could not establish is whether any of this helped. Attendance is not an outcome. To "
     "know whether the rooms improved anybody's Finnish or their chances of finding work, the service "
     "would have to follow people after they stopped coming, and it has never had either the permission "
     "or the money to do so. Virtanen is careful on this point. The rooms, she says, are well used, "
     "cheap, and popular, and not one of those three facts is evidence of effectiveness. A service can "
     "be all three and still make no measurable difference to the problem it was created to solve."),

    ("Buying a little more meaning",
     "The recommendation Tampere accepted in 2024 was deliberately modest. Rather than commission an "
     "outcome study it could not afford, the service added two boxes to the existing paper sheet: first "
     "visit or return visit, and the year in which the visitor first arrived in Finland. Each takes a "
     "tutor about three seconds to tick. Neither answers the question of effectiveness. Together, "
     "though, they turn a raw tally into something that can be compared between one room and another and "
     "between one year and the next. Virtanen describes this as buying a little more meaning at almost "
     "no cost, which she regards as the most that most small services can honestly expect."),
]

Q243 = [
    ("multiple_choice", "detail", 1,
     "because the caretaker needed to know when the building could be locked",
     "Why did staff originally log each visit on a paper sheet?",
     ["To report visitor numbers to the city council.",
      "So that the caretaker would know when the building could be locked.",
      "To measure whether the service was working.",
      "Because the libraries had no computers available."],
     "B",
     "Paragraph 1 states the reason directly, and then emphasises that the record was created for a "
     "purpose unconnected with measurement."),

    ("true_false_not_given", "detail", 1,
     "nobody expected the service to be evaluated",
     "The Iltatupa rooms were set up with a plan for evaluating them.",
     None, "FALSE",
     "Paragraph 1 states that nobody expected the service to be evaluated when the first room opened "
     "in 2015."),

    ("matching_information", "reference", 2,
     "equally consistent with thirty-eight thousand people attending once",
     "Which paragraph shows that one reported total could describe two very different services?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 2",
     "Paragraph 2 sets out the ambiguity: the same total fits many one-off visitors and a few very "
     "frequent ones."),

    ("sentence_completion", "detail", 1,
     "a tutor for three hours on weekday evenings",
     "Complete the sentence: Each room provides a tutor for ____ hours on weekday evenings.",
     None, "three",
     "Paragraph 1 describes each Iltatupa as a table and a tutor for three hours on weekday evenings.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "They do not record names",
     "What information about visitors do the paper sheets fail to record?",
     None, "names",
     "Paragraph 2 states that the sheets do not record names, which is why repeat visitors cannot be "
     "identified.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 2,
     "The tally could not tell them apart",
     "What was Virtanen's criticism of the 2022 figure?",
     ["It had been added up incorrectly.",
      "It could not distinguish many occasional visitors from a few frequent ones.",
      "It left out visits made at weekends.",
      "It was based on an unrepresentative sample of rooms."],
     "B",
     "Paragraph 2 explains that the total was equally consistent with two very different patterns of "
     "use, and that the tally could not tell them apart. The arithmetic itself was never in question."),

    ("true_false_not_given", "detail", 3,
     "tutors in four rooms asked every visitor one thing as they arrived",
     "The 2023 study relied on tutors putting a question to visitors in person.",
     None, "TRUE",
     "Paragraph 3 describes tutors in four rooms asking every visitor, as they arrived, whether they "
     "had been before."),

    ("matching_information", "reference", 4,
     "not one of those three facts is evidence of effectiveness",
     "Which paragraph argues that being popular is not the same as being effective?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 4",
     "Paragraph 4 lists three positive facts about the rooms and states that none of them is evidence "
     "of effectiveness."),

    ("sentence_completion", "detail", 3,
     "about 62% of visits were made by people who had already attended at least five times",
     "Complete the sentence: The study suggested that about ____ of visits were made by people who had "
     "already attended at least five times.",
     None, "62%",
     "Paragraph 3 reports this figure as the study's central finding.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 3,
     "tutors in four rooms",
     "In how many rooms was the 2023 study carried out?",
     None, "four",
     "Paragraph 3 states that tutors in four rooms took part in the six-week study.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "writer_purpose", 4,
     "well used, cheap, and popular",
     "Why does Virtanen describe the rooms as 'well used, cheap, and popular'?",
     ["To recommend that the service be expanded to more libraries.",
      "To point out that none of these facts shows that the service works.",
      "To justify the cost of the 2023 study.",
      "To compare the rooms with services in other Finnish cities."],
     "B",
     "The list is immediately followed by the statement that not one of the three facts is evidence of "
     "effectiveness. The purpose is to separate popularity from proof."),

    ("true_false_not_given", "detail", 4,
     "the service would have to follow people after they stopped coming",
     "The service has tracked visitors after they stopped attending.",
     None, "FALSE",
     "Paragraph 4 states that such follow-up would be necessary but that the service has never had "
     "either the permission or the money for it."),

    ("matching_information", "reference", 5,
     "the service added two boxes to the existing paper sheet",
     "Which paragraph describes a low-cost change to the way information is collected?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 5",
     "Paragraph 5 describes adding two tick-boxes to the existing sheet instead of commissioning a "
     "study."),

    ("sentence_completion", "detail", 5,
     "Each takes a tutor about three seconds to tick",
     "Complete the sentence: Each new box takes a tutor about ____ seconds to tick.",
     None, "three",
     "Paragraph 5 gives three seconds as the time required for each box.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 3,
     "For six weeks",
     "For how many weeks did the 2023 study run?",
     None, "six",
     "Paragraph 3 states that the study ran for six weeks.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "main_idea", 1,
     "They were designed for a purpose that had nothing whatever to do with measuring anything",
     "What is the main point of the first paragraph?",
     ["The rooms proved popular from the moment they opened.",
      "The service's only long record was created for a completely unrelated practical reason.",
      "Libraries in Tampere were short of qualified staff.",
      "The service expanded from one room to eleven in nine years."],
     "B",
     "The paragraph builds to its final sentence: the sheets that now serve as the service's evidence "
     "were created so that a caretaker would know when to lock up."),

    ("true_false_not_given", "inference", 1,
     "the city library service in Tampere opened its first Iltatupa",
     "Other Finnish cities have copied the Iltatupa model.",
     None, "NOT GIVEN",
     "The passage describes only the Tampere service. It says nothing about whether the model has been "
     "adopted elsewhere."),

    ("matching_information", "reference", 3,
     "Virtanen's team ran a small study in 2023 to settle the question",
     "Which paragraph describes how a specific ambiguity in the data was resolved?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 3",
     "Paragraph 3 reports the 2023 study, which was run specifically to settle the question raised in "
     "paragraph 2."),

    ("sentence_completion", "detail", 2,
     "record a date, a room, and a tally",
     "Complete the sentence: The paper sheets record a date, a room, and a ____.",
     None, "tally",
     "Paragraph 2 lists exactly these three items as everything the sheets contain.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 5,
     "The recommendation Tampere accepted in 2024",
     "In which year did Tampere accept Virtanen's recommendation?",
     None, "2024",
     "Paragraph 5 states that the recommendation was accepted in 2024.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 5,
     "the most that most small services can honestly expect",
     "What does Virtanen consider realistic for most small services?",
     ["Commissioning a full outcome study every few years.",
      "Gaining a little more meaning from existing records at almost no cost.",
      "Replacing paper records with a digital system.",
      "Employing a researcher on a permanent basis."],
     "B",
     "Paragraph 5 records her view that buying a little more meaning at almost no cost is the most "
     "that most small services can honestly expect."),

    ("true_false_not_given", "inference", 5,
     "they turn a raw tally into something that can be compared between one room and another",
     "The two new boxes will make it possible to compare one room with another.",
     None, "TRUE",
     "Paragraph 5 states that the two boxes together allow comparison between rooms and between "
     "years."),

    ("matching_information", "reference", 1,
     "free help with Finnish, job applications, and government websites",
     "Which paragraph explains what an Iltatupa offers its visitors?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 1",
     "Paragraph 1 lists the table, the tutor, and free help with Finnish, job applications and "
     "government websites."),

    ("sentence_completion", "main_idea", 4,
     "Attendance is not an outcome",
     "Complete the sentence: Virtanen's objection rests on a simple distinction: attendance is not an "
     "____.",
     None, "outcome",
     "Paragraph 4 states the distinction in a single short sentence: attendance is not an outcome.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "Dr Hanna Virtanen of Tampere University",
     "At which university does Dr Hanna Virtanen work?",
     None, "Tampere University",
     "Paragraph 2 identifies her as Dr Hanna Virtanen of Tampere University.",
     "NO MORE THAN TWO WORDS"),
]


# --------------------------------------------------------------------------
# B2-244 - Waikato Learning Trust, Hamilton: future choices and governance
# --------------------------------------------------------------------------

P244 = [
    ("Nobody wrote down who decides",
     "The Waikato Learning Trust in Hamilton, New Zealand, was set up in 2012 by five secondary schools "
     "and a community house that had been sharing tutors informally for years. Its founding document "
     "runs to two pages. It names the trustees and sets out how money is to be handled, and it says "
     "nothing at all about who may close a site, change what is taught, or turn down a new partner. In "
     "2012 this hardly mattered, because there were four tutors and one venue and everybody involved "
     "knew everybody else. By 2024 the trust employed 31 staff across nine sites and served about 2,600 "
     "learners a year."),

    ("Two kinds of authority",
     "Two groups now take decisions, and only one of them appears in the founding document. The trustees "
     "meet six times a year and control the budget. The site coordinators, who are not trustees, decide "
     "what is actually taught, when sessions run, and which learners get a place when a class is full. "
     "Neither group can easily overrule the other. A trustee can withhold money from a site; a "
     "coordinator can decline to run a course the trustees have funded. In eleven years this has "
     "produced open conflict only twice, largely because the two groups have wanted the same things."),

    ("The argument about the Saturday sites",
     "The exception came in 2023, over three Saturday-only sites in outlying towns. Together they cost "
     "the trust NZ$96,000 a year and served 190 learners. That worked out at NZ$505 a learner, "
     "against NZ$310 at the Hamilton sites. The trustees wanted to close two of the three. The "
     "coordinators refused to draw up a closure plan, arguing that the learners concerned had no "
     "alternative within an hour's drive. Both sides used exactly the same cost figures. What they "
     "disagreed about was whether cost per learner is the right measure at all when the alternative for "
     "some learners is nothing."),

    ("Deciding by not deciding",
     "No vote was ever held. The trustees did not force the issue and the coordinators never produced "
     "the plan. Instead the 2024 budget funded the Saturday sites for one further year 'pending review', "
     "and the same wording appeared again in 2025. One of the three sites has since closed anyway, "
     "because its only tutor moved to Auckland and no replacement could be found. The outcome that "
     "neither group was willing to vote for has therefore begun to happen on its own, one resignation at "
     "a time. Nobody has described this as a decision, which is precisely what makes it so hard to "
     "challenge."),

    ("What a written rule would cost",
     "The obvious remedy is to rewrite the founding document and state plainly who decides what. A "
     "working group proposed exactly that in 2024. The objection came from an unexpected direction: "
     "three long-serving coordinators argued that their influence rests on the fact that it has never "
     "been written down, and that any document setting out a formal process would hand the final word to "
     "the trustees, who control the money. They may well be right. The trust's most valued feature — "
     "that decisions are taken close to the learners — has survived partly because nobody has ever had "
     "to defend it in writing."),
]

Q244 = [
    ("multiple_choice", "detail", 1,
     "it says nothing at all about who may close a site",
     "What does the trust's founding document fail to specify?",
     ["How many trustees the trust should have.",
      "Who has the authority to close a site or change what is taught.",
      "How the trust's money is to be handled.",
      "Which organisations were involved in setting it up."],
     "B",
     "Paragraph 1 states that the document names the trustees and covers money, but says nothing about "
     "who may close a site, change what is taught, or turn down a partner. Options A, C and D are all "
     "things the document does cover."),

    ("true_false_not_given", "detail", 1,
     "the trust employed 31 staff across nine sites",
     "By 2024 the trust employed more than thirty staff.",
     None, "TRUE",
     "Paragraph 1 gives the 2024 figure as 31 staff across nine sites."),

    ("matching_information", "reference", 2,
     "decide what is actually taught, when sessions run, and which learners get a place",
     "Which paragraph explains what the site coordinators control?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 2",
     "Paragraph 2 lists the coordinators' powers and contrasts them with the trustees' control of the "
     "budget."),

    ("sentence_completion", "detail", 1,
     "Its founding document runs to two pages",
     "Complete the sentence: The trust's founding document runs to ____ pages.",
     None, "two",
     "Paragraph 1 states that the founding document runs to two pages.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 1,
     "was set up in 2012 by five secondary schools",
     "In which year was the Waikato Learning Trust set up?",
     None, "2012",
     "Paragraph 1 states that the trust was set up in 2012.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 2,
     "largely because the two groups have wanted the same things",
     "Why has open conflict between the two groups been rare?",
     ["The trustees have always had the final word.",
      "The two groups have generally wanted the same things.",
      "The founding document sets out a clear process for settling disputes.",
      "The coordinators are themselves trustees."],
     "B",
     "Paragraph 2 attributes the rarity of conflict to agreement about priorities, not to any rule. "
     "The paragraph explicitly states that neither group can easily overrule the other."),

    ("true_false_not_given", "detail", 2,
     "only one of them appears in the founding document",
     "The site coordinators are named as decision-makers in the founding document.",
     None, "FALSE",
     "Paragraph 2 states that of the two groups now taking decisions, only one appears in the founding "
     "document, and paragraph 1 makes clear that the document names the trustees."),

    ("matching_information", "reference", 3,
     "That worked out at NZ$505 a learner",
     "Which paragraph compares the cost of serving learners in different places?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 3",
     "Paragraph 3 sets the cost per learner at the Saturday sites against the cost at the Hamilton "
     "sites."),

    ("sentence_completion", "detail", 2,
     "The trustees meet six times a year and control the budget",
     "Complete the sentence: The trustees meet ____ times a year and control the budget.",
     None, "six",
     "Paragraph 2 states that the trustees meet six times a year.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 3,
     "served 190 learners",
     "How many learners did the three Saturday-only sites serve?",
     None, "190",
     "Paragraph 3 states that the three sites together served 190 learners.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "main_idea", 3,
     "whether cost per learner is the right measure at all",
     "What did the trustees and coordinators actually disagree about in 2023?",
     ["Whether the cost figures had been calculated correctly.",
      "Whether cost per learner is the right measure when some learners have no alternative.",
      "How many Saturday sites the trust should operate in total.",
      "Whether the coordinators should be paid more for weekend work."],
     "B",
     "Paragraph 3 states that both sides used exactly the same figures, so the dispute was not about "
     "arithmetic but about whether cost per learner is the appropriate measure."),

    ("true_false_not_given", "detail", 3,
     "Both sides used exactly the same cost figures",
     "The coordinators disputed the accuracy of the trustees' cost figures.",
     None, "FALSE",
     "Paragraph 3 states that both sides used exactly the same cost figures."),

    ("matching_information", "reference", 4,
     "The outcome that neither group was willing to vote for",
     "Which paragraph describes an outcome that came about without anyone voting for it?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 4",
     "Paragraph 4 describes a site closing through a resignation rather than through any decision."),

    ("sentence_completion", "detail", 3,
     "against NZ$310 at the Hamilton sites",
     "Complete the sentence: Serving a learner cost NZ$505 at the Saturday sites, against NZ$____ "
     "at the Hamilton sites.",
     None, "310",
     "Paragraph 3 gives NZ$310 a learner as the Hamilton figure.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 4,
     "its only tutor moved to Auckland",
     "To which city did the tutor at the closed site move?",
     None, "Auckland",
     "Paragraph 4 explains that the site closed because its only tutor moved to Auckland.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "writer_purpose", 4,
     "Nobody has described this as a decision",
     "Why does the writer point out that 'Nobody has described this as a decision'?",
     ["To show that the trustees had acted beyond their authority.",
      "To suggest that an outcome nobody chose is very difficult to challenge.",
      "To criticise the coordinators for refusing to produce a plan.",
      "To explain why the 2024 budget was delayed."],
     "B",
     "The observation completes the paragraph's argument: because the closure was never framed as a "
     "decision, there is nothing for an objector to argue against."),

    ("true_false_not_given", "inference", 4,
     "the same wording appeared again in 2025",
     "The trust has considered merging with a similar organisation in Auckland.",
     None, "NOT GIVEN",
     "Auckland is mentioned only as the place a tutor moved to. The passage says nothing about any "
     "proposed merger."),

    ("matching_information", "reference", 5,
     "The objection came from an unexpected direction",
     "Which paragraph reports an objection from an unexpected source?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 5",
     "Paragraph 5 records that the objection to a written rule came from the coordinators themselves, "
     "not from the trustees."),

    ("sentence_completion", "detail", 4,
     "for one further year 'pending review'",
     "Complete the sentence: The 2024 budget funded the Saturday sites for one further year, pending "
     "____.",
     None, "review",
     "Paragraph 4 quotes the budget wording as 'pending review', repeated again in 2025.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "this has produced open conflict only twice",
     "How many times in eleven years has open conflict arisen between the two groups?",
     None, "twice",
     "Paragraph 2 states that open conflict has arisen only twice in eleven years.",
     "NO MORE THAN ONE WORD"),

    ("multiple_choice", "inference", 5,
     "would hand the final word to the trustees, who control the money",
     "Why do three long-serving coordinators oppose putting the rules in writing?",
     ["They believe a formal process would give the trustees the final word.",
      "They think the founding document is already clear enough.",
      "They want the trust to expand more quickly than the trustees allow.",
      "They object to the cost of redrafting the document."],
     "A",
     "Paragraph 5 reports their argument that their influence depends on the rules being unwritten, "
     "and that a formal process would hand the final word to the trustees, who control the money."),

    ("true_false_not_given", "detail", 5,
     "A working group proposed exactly that in 2024",
     "A working group recommended rewriting the trust's founding document.",
     None, "TRUE",
     "Paragraph 5 states that a working group proposed rewriting the document in 2024."),

    ("matching_information", "reference", 1,
     "By 2024 the trust employed 31 staff across nine sites",
     "Which paragraph describes how the trust grew between 2012 and 2024?",
     ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
     "Paragraph 1",
     "Paragraph 1 contrasts four tutors at one venue in 2012 with 31 staff across nine sites in 2024."),

    ("sentence_completion", "main_idea", 5,
     "that decisions are taken close to the learners",
     "Complete the sentence: The trust's most valued feature is that decisions are taken close to the "
     "____.",
     None, "learners",
     "Paragraph 5 identifies this as the trust's most valued feature.",
     "NO MORE THAN ONE WORD"),

    ("short_answer", "detail", 2,
     "which learners get a place when a class is full",
     "Who decides which learners get a place when a class is full?",
     None, "site coordinators",
     "Paragraph 2 states that the site coordinators decide who gets a place when a class is full.",
     "NO MORE THAN TWO WORDS"),
]


BUILD = {
    "B2-241": (P241, Q241),
    "B2-242": (P242, Q242),
    "B2-243": (P243, Q243),
    "B2-244": (P244, Q244),
}


def normalize(s):
    """Mirror of the normalize() used for grading in js/app.js."""
    s = str(s).lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "N") or ch.isspace():
            out.append(ch)
        else:
            out.append(" ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


def build_questions(spec, paragraphs):
    questions = []
    answer_key = []
    for i, item in enumerate(spec):
        qtype, skill, para, anchor, prompt, options, answer, explanation = item[:8]
        word_limit = item[8] if len(item) > 8 else None
        heading = paragraphs[para - 1][0]
        qid = "Q%02d" % (i + 1)

        q = {
            "id": qid,
            "type": qtype,
            "skill": skill,
            "difficulty": "B2",
            "evidence": {"paragraph": para, "heading": heading, "anchor": anchor},
            "explanation": explanation,
        }

        if qtype == "true_false_not_given":
            q["statement"] = prompt
        else:
            q["question"] = prompt

        if qtype == "multiple_choice":
            q["options"] = options
            q["answer"] = answer
            q["answer_text"] = options["ABCD".index(answer)]
        elif qtype == "matching_information":
            q["options"] = options
            q["answer"] = answer
        else:
            q["answer"] = answer

        if word_limit:
            q["word_limit"] = word_limit

        questions.append(q)
        answer_key.append({"id": qid, "answer": q["answer"], "explanation": explanation})

    return questions, answer_key


def validate(topic_id, paragraphs, questions):
    errs = []
    if len(questions) != 25:
        errs.append("%s: %d questions, expected 25" % (topic_id, len(questions)))

    counts = {}
    for q in questions:
        counts[q["type"]] = counts.get(q["type"], 0) + 1
    for t in ("multiple_choice", "true_false_not_given", "matching_information",
              "sentence_completion", "short_answer"):
        if counts.get(t) != 5:
            errs.append("%s: %s appears %s times, expected 5" % (topic_id, t, counts.get(t, 0)))

    tfng = [q["answer"] for q in questions if q["type"] == "true_false_not_given"]
    for verdict in ("TRUE", "FALSE", "NOT GIVEN"):
        if verdict not in tfng:
            errs.append("%s: no %s among the True/False/Not Given items" % (topic_id, verdict))

    for q in questions:
        ev = q["evidence"]
        para_heading, para_text = paragraphs[ev["paragraph"] - 1]
        if ev["heading"] != para_heading:
            errs.append("%s %s: heading mismatch" % (topic_id, q["id"]))
        # app.js highlights the anchor with a literal split, so it must be present verbatim.
        if ev["anchor"] not in para_text:
            errs.append("%s %s: anchor not found verbatim in paragraph %d: %r"
                        % (topic_id, q["id"], ev["paragraph"], ev["anchor"]))

        if q["type"] == "multiple_choice":
            if q["answer"] not in "ABCD" or len(q["options"]) != 4:
                errs.append("%s %s: bad multiple-choice answer/options" % (topic_id, q["id"]))
            elif q["answer_text"] != q["options"]["ABCD".index(q["answer"])]:
                errs.append("%s %s: answer_text does not match the keyed option" % (topic_id, q["id"]))
        elif q["type"] == "matching_information":
            if q["answer"] not in q["options"]:
                errs.append("%s %s: keyed answer is not one of the options" % (topic_id, q["id"]))
        elif q["type"] == "true_false_not_given":
            if q["answer"] not in ("TRUE", "FALSE", "NOT GIVEN"):
                errs.append("%s %s: bad TFNG answer" % (topic_id, q["id"]))
        else:
            if not normalize(q["answer"]):
                errs.append("%s %s: answer normalises to nothing" % (topic_id, q["id"]))
            limit = int(re.search(r"(ONE|TWO|THREE|FOUR)", q["word_limit"]).group(1)
                        .replace("ONE", "1").replace("TWO", "2")
                        .replace("THREE", "3").replace("FOUR", "4"))
            if len(normalize(q["answer"]).split()) > limit:
                errs.append("%s %s: keyed answer exceeds its own word limit" % (topic_id, q["id"]))

    return errs


def main():
    all_errs = []
    for topic_id, filename in FILES.items():
        paragraphs, qspec = BUILD[topic_id]
        path = os.path.join(DATA, filename)
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)

        sections = []
        full_parts = []
        for i, (heading, text) in enumerate(paragraphs):
            sections.append({"paragraph": i + 1, "heading": heading, "text": text})
            full_parts.append("Paragraph %d — %s\n%s" % (i + 1, heading, text))

        questions, answer_key = build_questions(qspec, paragraphs)
        errs = validate(topic_id, paragraphs, questions)
        all_errs.extend(errs)
        if errs:
            continue

        doc["passage"]["sections"] = sections
        doc["passage"]["full_text"] = "\n\n".join(full_parts)
        doc["question_count"] = len(questions)
        doc["questions"] = questions
        doc["answer_key"] = answer_key

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)

        words = len(doc["passage"]["full_text"].split())
        print("%s  %s  %d words, %d questions" % (topic_id, filename[:34], words, len(questions)))

    if all_errs:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in all_errs:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    print("\nAll four files written and validated.")


if __name__ == "__main__":
    main()
