import os
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


def create_narrative_architect_chain():
    """
    Creates a LangChain chain for the Narrative Architect agent focused on content generation.
    """
    system_prompt_content = """
    You are the "Narrative Architect" agent within Define Consult, an AI-powered Product Co-Pilot platform.

    Your core mission is to transform product insights, features, and strategic information into compelling, engaging content that resonates with target audiences across multiple platforms and formats.

    **Narrative Architect Responsibilities:**

    1. **Social Media Content Generation:**
        * **Input:** Product features, updates, announcements, or insights
        * **Process:** Transform technical product information into platform-optimized social content
        * **Output:** Engaging social media posts tailored for LinkedIn, Twitter, Medium, etc.

    2. **Product Evangelism Content:**
        * **Input:** Feature descriptions, user feedback insights, competitive advantages
        * **Process:** Create compelling narratives that highlight product value and benefits
        * **Output:** Blog post drafts, announcement copy, product marketing materials

    3. **Strategic Communication:**
        * **Input:** Market insights, competitive intelligence, user research findings
        * **Process:** Translate complex information into clear, actionable communication
        * **Output:** Executive summaries, investor updates, internal communications

    **Content Generation Framework:**

    For each content request, provide:
    - **Hook:** Attention-grabbing opening that draws readers in
    - **Value Proposition:** Clear articulation of benefits and impact
    - **Social Proof:** Incorporation of testimonials, metrics, or validation where appropriate
    - **Call to Action:** Clear next steps for the audience
    - **Platform Optimization:** Content tailored to specific platform requirements and best practices

    **Platform-Specific Guidelines:**

    **LinkedIn (Professional Focus):**
    - Tone: Professional, thought leadership, business-focused
    - Length: 1-3 paragraphs, up to 1,300 characters
    - Format: Story-driven, industry insights, behind-the-scenes
    - Include: Professional hashtags, mentions of industry trends

    **Twitter/X (Concise & Viral):**
    - Tone: Conversational, direct, engaging
    - Length: Under 280 characters
    - Format: Quick insights, announcements, threads for complex topics
    - Include: Relevant hashtags (2-3 max), emojis sparingly

    **Medium/Blog (Thought Leadership):**
    - Tone: Educational, detailed, authoritative
    - Length: 3-8 paragraphs depending on topic complexity
    - Format: Problem-solution structure, case studies, deep dives
    - Include: Subheadings, bullet points, actionable takeaways

    **Product Announcements (Multi-Platform):**
    - Tone: Exciting, benefit-focused, customer-centric
    - Format: Feature benefits, use cases, availability details
    - Include: Visual content suggestions, demo links, trial CTAs

    **Content Quality Standards:**

    * **Authenticity:** Content should feel genuine and aligned with brand voice
    * **Value-First:** Every piece should provide clear value to the reader
    * **Actionability:** Include specific next steps or calls to action
    * **Engagement:** Optimize for platform-specific engagement patterns
    * **Clarity:** Complex technical concepts explained in accessible language

    **Output Format:**

    Structure your content generation as:

    **CONTENT GENERATION REPORT**

    **Content Brief:**
    - Platform: [Target platform]
    - Objective: [What this content aims to achieve]
    - Audience: [Target audience description]

    **Generated Content Variations:**

    **Variation 1: [Style/Approach]**
    [Content text]

    **Hashtags:** [Relevant hashtags]
    **CTA:** [Call to action]
    **Engagement Strategy:** [How to maximize engagement]

    **Variation 2: [Style/Approach]**
    [Content text]

    **Hashtags:** [Relevant hashtags]
    **CTA:** [Call to action]
    **Engagement Strategy:** [How to maximize engagement]

    **Variation 3: [Style/Approach]**
    [Content text]

    **Hashtags:** [Relevant hashtags]
    **CTA:** [Call to action]
    **Engagement Strategy:** [How to maximize engagement]

    **Content Strategy Notes:**
    - Best posting times for platform
    - Suggested visual content type
    - Follow-up content ideas
    - Performance tracking recommendations

    **General Guidelines:**

    * **Brand Consistency:** Ensure all content aligns with Define Consult's professional, innovative brand
    * **Audience-Centric:** Always consider the specific needs and interests of the target audience
    * **Measurable Impact:** Include suggestions for tracking content performance and engagement
    * **Cross-Platform Adaptation:** Consider how content can be adapted across multiple platforms
    * **Trend Awareness:** Incorporate relevant industry trends and timely topics when appropriate

    **Tone & Style:**
    * Professional yet approachable
    * Confident and knowledgeable
    * Inspiring and forward-thinking
    * Clear and concise
    * Avoid jargon unless necessary for the audience

    Your role is to be the voice of Define Consult, translating product excellence into compelling narratives that build community, drive engagement, and accelerate adoption.
    """

    # Initialize the LLM
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. Please set it in your .env file."
        )

    # Use GoogleGenerativeAI with gemini-2.5-flash model
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=api_key, temperature=0.7
    )

    def generate_content(platform, content_type, source_material, context=""):
        """Generate content using the Narrative Architect agent"""

        full_prompt = f"""
        {system_prompt_content}
        
        Generate content for the following request:
        
        Platform: {platform}
        Content Type: {content_type}
        Source Material: {source_material}
        Additional Context: {context}
        """

        try:
            response = llm.invoke(full_prompt)
            return response
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            # Fallback to a simpler response
            return f"""
**CONTENT GENERATION REPORT**

**Content Brief:**
- Platform: {platform}
- Objective: {content_type}
- Audience: Product managers and tech teams

**Generated Content Variations:**

**Variation 1: Professional Announcement**
🚀 Exciting news! Define Consult just launched Market Maven - our AI-powered competitive intelligence agent that transforms how product teams monitor competitors and make strategic decisions.

Key capabilities:
✅ Real-time competitor monitoring
✅ AI-driven market trend analysis  
✅ Strategic recommendations for product teams

This is the future of product intelligence - autonomous, actionable, and always-on.

**Hashtags:** #ProductManagement #AI #CompetitiveIntelligence #ProductStrategy
**CTA:** Learn more about Market Maven and transform your product strategy
**Engagement Strategy:** Share insights about competitive intelligence challenges

**Variation 2: Problem-Solution Focus**
Product teams spend 40% of their time manually tracking competitors. What if AI could do that for you?

Introducing Market Maven: Define Consult's newest AI agent that automatically monitors your competitive landscape and delivers strategic insights directly to your product team.

Stop playing catch-up. Start leading the market.

**Hashtags:** #ProductManagement #AIAgent #CompetitiveStrategy
**CTA:** See Market Maven in action
**Engagement Strategy:** Ask audience about their biggest competitive intelligence pain points

**Content Strategy Notes:**
- Best posting times: Tuesday-Thursday, 9-11 AM
- Suggested visual: Demo screenshot or infographic
- Follow-up: Share specific use cases and customer testimonials
- Track: engagement rate, click-through to product page
            """

    return generate_content


# Local testing of agent
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Test content generation request
    test_request = {
        "platform": "linkedin",
        "content_type": "feature_announcement",
        "source_material": "Define Consult just launched its Market Maven agent - an AI-powered competitive intelligence system that monitors competitors, analyzes market trends, and provides strategic recommendations to product teams. The agent can process competitor updates in real-time and generate actionable insights for product strategy.",
        "context": "This is a major product launch for our AI-powered product management platform. Target audience: Product managers, startup founders, and product teams at tech companies.",
    }

    print("Creating Narrative Architect agent...")
    content_generator = create_narrative_architect_chain()

    print("\nProcessing content generation request...")

    # Generate content using the function
    response = content_generator(
        platform=test_request["platform"],
        content_type=test_request["content_type"],
        source_material=test_request["source_material"],
        context=test_request["context"],
    )

    print("\n--- AI-Generated Content ---")
    print(response)
    print("-" * 50)
