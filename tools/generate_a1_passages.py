#!/usr/bin/env python3
"""
Generate 80 A1 passages with 5 questions each.
Creates passages for A1_001 to A1_080 covering 20 domains (4 per domain).
"""

import json
from pathlib import Path

DOMAINS = [
    ("Education", "Community Learning Centres"),
    ("Environment", "River Restoration Projects"),
    ("Technology", "Responsible Digital Services"),
    ("Health", "Everyday Wellbeing Programmes"),
    ("Travel", "Regional Transport Networks"),
    ("Arts", "Neighbourhood Arts Festivals"),
    ("Science", "Public Observation Projects"),
    ("Work", "Flexible Workplace Practices"),
    ("Food", "Sustainable Community Kitchens"),
    ("Urban Design", "Human Centred Public Spaces"),
    ("Culture", "Preservation of Local Archives"),
    ("Languages", "Multilingual Public Information"),
    ("Business", "Small Business Resilience Plans"),
    ("Agriculture", "Climate Aware Farming Methods"),
    ("Energy", "Local Energy Saving Initiatives"),
    ("Maritime", "Coastal Monitoring Programmes"),
    ("Psychology", "Attention and Learning Habits"),
    ("Architecture", "Adaptive Reuse of Old Buildings"),
    ("Communication", "Community Information Networks"),
    ("Wildlife", "Urban Wildlife Corridors"),
]

FOCUSES = [
    ("origins", "The Story"),
    ("benefits", "Why It Helps"),
    ("measurement", "Tracking Success"),
    ("future", "What Comes Next"),
]

PASSAGE_TEMPLATES = {
    "origins": [
        "The {DOMAIN} programme began {YEARS} years ago. Local people saw a problem and wanted to change things. They decided to start a project together to help the community. Friends, family and volunteers worked as a team.",
        "Today the programme runs {DAYS} days every week. Helpers and staff work hard each day. Many people visit the centre. They come to learn and have fun. The programme offers different activities for different people.",
        "The number of people who come has grown each year. Hundreds of people now use the services. The programme is popular in the neighbourhood. People say they like the work. The project is now important to everyone.",
        "But there are still some problems. There is not much money to spend. The buildings need repairs sometimes. It is difficult to find enough volunteers. But people still believe in the work.",
        "The programme will change and grow in coming years. New services will start. More areas will have the programme. It will help many more people in the future."
    ],
    "benefits": [
        "People get many good things from the {DOMAIN} programme. They learn new skills and knowledge. They feel happier. They make new friends. Children, young people and adults all benefit.",
        "But there are also some difficulties. Some people find it hard to come regularly. It takes time and effort to join in. Some new people feel worried at first. Not everyone benefits in the same way.",
        "People often feel better after coming. They worry less and feel happier. They make good friends. They feel more confident about things. Their families notice the changes too.",
        "People find better jobs because of the skills they learn. Some people earn more money. Their lives become better and easier. They can support their families better. Everyone's future looks brighter.",
        "The good things that happen are worth the time and work. People are much happier. Families are stronger. The whole community benefits. Everyone gains something important."
    ],
    "measurement": [
        "The programme counts how many people come each month. They write down all the numbers. They ask people what they think about the work. They listen carefully to all feedback. This helps them make the programme better.",
        "The measurements show real changes happening. People learn new skills. They score better on tests. People report feeling more confident. Families say life is better now.",
        "The neighbourhood has changed because of the programme. Neighbours know each other better. People help each other more. The area feels safer. Fewer problems happen in the community.",
        "The money spent on the programme gives back much more. For every pound spent, many pounds come back. People spend more money in shops. They need less help from other services. It is good value for money.",
        "All the data and feedback show the programme works well. The results are very good. Everyone is happy with it. The evidence clearly shows it helps. The programme should continue and grow."
    ],
    "future": [
        "The programme will grow and improve greatly. New services will begin soon. It will help many more people. It will reach more neighbourhoods and communities.",
        "New technology will make the programme better. Computers will help people learn. The internet will let people join from home. Communication will be faster and easier. Things will be more modern.",
        "The programme will work with more organizations. Schools will help teach together. Businesses will give support and money. Hospitals and other services will work as partners. Networks will be much bigger.",
        "The programme needs to find more money. Governments may give grants. Rich people might make donations. Companies might offer sponsorship. Banks might help with loans.",
        "In the end, every neighbourhood will have a programme like this. Everyone will be healthier and happier. Communities will be strong and friendly. People will have good opportunities. The future will be much better for all."
    ]
}

Q_TEMPLATES = {
    "multiple_choice": [
        ("What is the main topic of this passage?", ["Money and business", "A {DOMAIN} programme that helps people", "How to build buildings", "Problems in the past"]),
        ("How long has the programme been running?", ["One year", "Two years", "{YEARS} years", "Ten years"]),
        ("How many days a week does the programme work?", ["Every day", "Three days", "{DAYS} days", "Only weekends"]),
        ("What do people say about the programme?", ["It is not popular", "It does not help", "They like it and think it is good", "Nobody comes"]),
        ("What will happen to the programme in the future?", ["It will close down", "It will stay the same", "It will grow and help more people", "Nobody knows"]),
    ],
    "true_false_not_given": [
        ("The programme helps people in the community.", "TRUE"),
        ("Many people now use the programme.", "TRUE"),
        ("The programme has no problems at all.", "FALSE"),
        ("Volunteers help at the programme.", "TRUE"),
        ("The programme will stop next year.", "FALSE"),
    ],
    "sentence_completion": [
        ("The {DOMAIN} programme began ____.", "years ago"),
        ("People feel ____ after coming to the programme.", "happier"),
        ("The neighbourhood has become ____ because of the programme.", "better"),
        ("New ____ will help the programme work better.", "technology"),
        ("The programme will help many ____ people in the future.", "more"),
    ],
    "short_answer": [
        ("Why did people start the {DOMAIN} programme?", "They saw a problem and wanted to help"),
        ("How do we know the programme works?", "We count people and listen to feedback"),
        ("Who works at the programme?", "Staff and volunteers"),
        ("What do people learn at the programme?", "New skills and knowledge"),
        ("Why is money important for the programme?", "To pay for services and repairs"),
    ],
    "matching_information": [
        ("Which paragraph describes how the programme started?", "Paragraph 1"),
        ("Which paragraph talks about how people feel after coming?", "Paragraph 3"),
        ("Which paragraph talks about money and costs?", "Paragraph 4"),
        ("Which paragraph talks about the future?", "Paragraph 5"),
        ("Which paragraph describes the problems?", "Paragraph 4"),
    ]
}

def create_passage(topic_id, domain, location, focus_key, focus_title):
    """Create a complete A1 passage JSON."""

    # Build passage sections
    sections = []
    headings = ["Background", "How it works", "Results and benefits", "Challenges", "The future"]

    templates = PASSAGE_TEMPLATES[focus_key]

    for i in range(5):
        text = templates[i]
        text = text.replace("{DOMAIN}", domain.lower())
        text = text.replace("{YEARS}", "five")
        text = text.replace("{DAYS}", "five")

        sections.append({
            "paragraph": i + 1,
            "heading": headings[i],
            "text": text
        })

    # Build full text
    full_text_parts = [f"Paragraph {s['paragraph']} — {s['heading']}\n{s['text']}" for s in sections]
    full_text = "\n\n".join(full_text_parts)

    # Generate 5 questions
    questions = []
    answer_key = []
    q_types = ["multiple_choice", "true_false_not_given", "sentence_completion", "short_answer", "matching_information"]

    q_templates_list = [
        Q_TEMPLATES["multiple_choice"],
        Q_TEMPLATES["true_false_not_given"],
        Q_TEMPLATES["sentence_completion"],
        Q_TEMPLATES["short_answer"],
        Q_TEMPLATES["matching_information"]
    ]

    for q_num in range(1, 6):
        q_id = f"Q{q_num:02d}"
        q_type = q_types[q_num - 1]

        # Get template for this question type
        template_list = q_templates_list[q_num - 1]
        template = template_list[(q_num - 1) % len(template_list)]

        if q_type == "multiple_choice":
            q_text, options = template
            q_text = q_text.replace("{DOMAIN}", domain.lower())
            q_text = q_text.replace("{YEARS}", "five")
            q_obj = {
                "id": q_id,
                "type": q_type,
                "skill": "detail",
                "difficulty": "A1",
                "evidence": {
                    "paragraph": 1,
                    "heading": sections[0]["heading"],
                    "anchor": "main information"
                },
                "explanation": f"The answer is in the passage.",
                "question": q_text,
                "options": options,
                "answer": "B",
                "answer_text": options[1]
            }
        elif q_type == "true_false_not_given":
            statement, answer = template
            q_obj = {
                "id": q_id,
                "type": q_type,
                "skill": "inference",
                "difficulty": "A1",
                "evidence": {
                    "paragraph": 1,
                    "heading": sections[0]["heading"],
                    "anchor": "statement verification"
                },
                "explanation": f"The passage says this is {answer.lower()}.",
                "statement": statement,
                "answer": answer
            }
        elif q_type == "sentence_completion":
            q_text, answer = template
            q_text = q_text.replace("{DOMAIN}", domain.lower())
            q_obj = {
                "id": q_id,
                "type": q_type,
                "skill": "detail",
                "difficulty": "A1",
                "evidence": {
                    "paragraph": 2,
                    "heading": sections[1]["heading"],
                    "anchor": "missing word"
                },
                "explanation": f"The answer is '{answer}'.",
                "question": q_text,
                "word_limit": "NO MORE THAN ONE WORD",
                "answer": answer
            }
        elif q_type == "short_answer":
            q_text, answer = template
            q_text = q_text.replace("{DOMAIN}", domain.lower())
            q_text = q_text.replace("{DAYS}", "five")
            q_obj = {
                "id": q_id,
                "type": q_type,
                "skill": "detail",
                "difficulty": "A1",
                "evidence": {
                    "paragraph": 3,
                    "heading": sections[2]["heading"],
                    "anchor": "answer information"
                },
                "explanation": f"The answer is '{answer}'.",
                "question": q_text,
                "word_limit": "NO MORE THAN TWO WORDS",
                "answer": answer
            }
        else:  # matching_information
            q_text, answer = template
            q_obj = {
                "id": q_id,
                "type": q_type,
                "skill": "reference",
                "difficulty": "A1",
                "evidence": {
                    "paragraph": 5,
                    "heading": sections[4]["heading"],
                    "anchor": "paragraph location"
                },
                "explanation": f"The answer is '{answer}'.",
                "question": q_text,
                "options": ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4", "Paragraph 5"],
                "answer": answer
            }

        questions.append(q_obj)
        answer_key.append({
            "id": q_id,
            "answer": q_obj.get("answer", "TRUE" if q_type == "true_false_not_given" else "B"),
            "explanation": q_obj["explanation"]
        })

    return {
        "dataset_version": "3.0-authored",
        "content_status": "Original IELTS-style practice; not official IELTS material.",
        "cefr": {
            "level": "A1",
            "label": "Beginner",
            "language_profile": [
                "very simple sentences",
                "high-frequency vocabulary",
                "concrete everyday topics"
            ]
        },
        "topic": {
            "id": topic_id,
            "domain": domain,
            "title": f"{domain}: {focus_title} in {location}",
            "focus": f"{domain.lower()} - {focus_key}"
        },
        "recommended_time_minutes": 20,
        "candidate_instructions": "Read all five sections. Answer Questions 1-5. Follow the stated word limits exactly.",
        "passage": {
            "sections": sections,
            "full_text": full_text
        },
        "question_count": 5,
        "questions": questions,
        "answer_key": answer_key,
        "metadata": {
            "created": "2026-07-14",
            "encoding": "UTF-8",
            "intended_use": [
                "self-study",
                "question-bank import",
                "teacher adaptation"
            ],
            "tags": [
                "A1",
                domain.lower(),
                focus_key,
                "reading",
                "IELTS-style"
            ]
        }
    }

def main():
    """Generate all 80 A1 passages."""
    data_dir = Path("data")
    a1_dir = data_dir / "A1"
    a1_dir.mkdir(parents=True, exist_ok=True)

    passage_id = 1
    print(f"Generating 80 A1 passages (A1_001 to A1_080)...")

    for domain, location in DOMAINS:
        for focus_key, focus_title in FOCUSES:
            # Create topic ID
            topic_id = f"A1-{passage_id:03d}"

            # Create passage
            passage_json = create_passage(
                topic_id,
                domain,
                location,
                focus_key,
                focus_title
            )

            # Create filename - slugify title
            domain_slug = domain.lower().replace(" ", "_")
            focus_slug = focus_key.lower()
            location_slug = location.lower().replace(" ", "_")
            filename = f"A1_{passage_id:03d}_{domain_slug}_{focus_slug}_{location_slug}.json"

            filepath = a1_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(passage_json, f, indent=2, ensure_ascii=False)

            if passage_id % 20 == 0:
                print(f"  ✓ {passage_id}/80 passages created")

            passage_id += 1

    print(f"✓ Successfully generated 80 A1 passages!")
    print(f"Files saved in data/A1/")

if __name__ == "__main__":
    main()
