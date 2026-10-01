def build_comic_layout(
    stories,
    image_paths,
):

    layout = []

    for index, story in enumerate(stories):

        image_path = ""

        if index < len(image_paths):
            image_path = image_paths[index]

        layout.append(
            {
                "panel_number": story.get(
                    "panel_number",
                    index + 1,
                ),
                "title": story.get(
                    "title",
                    f"Panel {index + 1}",
                ),
                "scene_description": story.get(
                    "scene_description",
                    "",
                ),
                "image_prompt": story.get(
                    "image_prompt",
                    "",
                ),
                "caption": story.get(
                    "caption",
                    "",
                ),
                "narration": story.get(
                    "narration",
                    "",
                ),
                "dialogue": story.get(
                    "dialogue",
                    "",
                ),
                "image_path": image_path,
            }
        )

    return layout