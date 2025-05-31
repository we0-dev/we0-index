#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/2/20
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : prompt
# @Software: PyCharm
class SystemPrompt:
    ANALYZE_CODE_PROMPT = """
    # Task Instructions
    1. I will provide a code block wrapped in ```
    2. Analyze the code with these steps:
       - Identify natural segments separated by empty lines, comment blocks, or logical sections
       - Generate technical descriptions for each segment
    3. Output requirements:
       - Use numbered Markdown lists (1. 2. 3.)
       - Maximum 2 lines per item
       - Prioritize functional explanations, then implementation details
       - Preserve key technical terms/algorithms
       - Keep identical terminology with source code
    
    # Output Example
    1. Initializes Spring Boot application: Uses @SpringBootApplication to configure bootstrap class, sets base package for component scanning
    2. Implements RESTful endpoint: Creates /user API through @RestController, defines base path with @RequestMapping
    3. Handles file uploads: Leverages S3 SDK to transfer local file_infos to cloud storage
    
    # Now analyze this code:*
    """


class SystemMessageTemplate:
    ANALYZE_CODE_MESSAGE_TEMPLATE = lambda code_text: [
        {
            "role": "system",
            "content": SystemPrompt.ANALYZE_CODE_PROMPT
        },
        {
            "role": "user",
            "content": code_text
        }
    ]
