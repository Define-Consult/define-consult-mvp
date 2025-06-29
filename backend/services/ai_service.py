"""
AI Service Module for Define Consult MVP

This module handles all AI operations including:
- OpenRouter API interactions (free models)
- LangChain Google Generative AI interactions
- Prompt engineering for different agents
- Content processing and generation
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Union
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize AI clients
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini via LangChain
langchain_gemini = None
if gemini_api_key:
    langchain_gemini = GoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=gemini_api_key, temperature=0.7
    )

logger = logging.getLogger(__name__)

# Models from OpenRouter
MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-r1-0528-qwen3-8b:free",
    "mistralai/mistral-7b-instruct:free",
]


class AIService:
    """Main AI service class for Define Consult agents"""

    def __init__(self):
        self.openrouter_api_key = openrouter_api_key
        self.langchain_gemini = langchain_gemini

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model_preference: str = "auto",
    ) -> str:
        """
        Generate AI completion using available AI service
        """
        try:
            # Choose best model based on context/preference
            if model_preference == "auto":
                model_preference = self._select_best_model(prompt)

            if self.openrouter_api_key and model_preference in MODELS:
                return await self._openrouter_completion(
                    prompt, max_tokens, temperature, model_preference
                )
            elif self.langchain_gemini:
                return await self._gemini_completion(prompt, max_tokens, temperature)
            else:
                raise Exception("No AI service available")
        except Exception as e:
            logger.error(f"AI completion error: {e}")
            # Fallback to Gemini if OpenRouter fails
            if self.langchain_gemini and model_preference != "gemini":
                logger.info("Falling back to Gemini API")
                return await self._gemini_completion(prompt, max_tokens, temperature)
            raise

    def _select_best_model(self, prompt: str) -> str:
        """
        Select the best model based on prompt context
        """
        prompt_lower = prompt.lower()

        # For complex analysis tasks, use Llama
        if any(
            word in prompt_lower
            for word in ["analyze", "extract", "complex", "detailed"]
        ):
            return "meta-llama/llama-3.1-8b-instruct:free"

        # For reasoning tasks, use DeepSeek R1
        elif any(
            word in prompt_lower for word in ["reason", "logic", "step", "problem"]
        ):
            return "deepseek/deepseek-r1:free"

        # For content generation, use Mistral
        elif any(
            word in prompt_lower for word in ["write", "generate", "create", "draft"]
        ):
            return "mistralai/mistral-7b-instruct:free"

        # Default to Llama for general tasks
        return "meta-llama/llama-3.1-8b-instruct:free"

    async def _openrouter_completion(
        self, prompt: str, max_tokens: int, temperature: float, model: str
    ) -> str:
        """Generate completion using OpenRouter"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://defineconsult.co",
                    "X-Title": "Define Consult",
                },
                data=json.dumps(
                    {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                ),
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(
                    f"OpenRouter API error: {response.status_code} - {response.text}"
                )

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    async def _gemini_completion(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Generate completion using Gemini via LangChain"""
        try:
            response = await self.langchain_gemini.agenerate([prompt])
            return response.generations[0][0].text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def analyze_transcript(self, content: str, context: Dict) -> Dict:
        """
        Analyze a customer feedback transcript using AI

        Args:
            content: The transcript content to analyze
            context: Additional context (title, user_id, etc.)

        Returns:
            Dict containing analysis results
        """
        try:
            # Create analysis prompt
            prompt = f"""
            Analyze the following customer feedback transcript and extract key insights:

            Title: {context.get('title', 'Customer Feedback')}
            Transcript:
            {content}

            Please provide a comprehensive analysis in JSON format with the following structure:
            {{
                "insights": [
                    "Key insight 1",
                    "Key insight 2",
                    "Key insight 3"
                ],
                "sentiment_score": 0.75,
                "key_themes": [
                    "Theme 1",
                    "Theme 2", 
                    "Theme 3"
                ],
                "pain_points": [
                    "Pain point 1",
                    "Pain point 2"
                ],
                "feature_requests": [
                    "Feature request 1",
                    "Feature request 2"
                ],
                "urgency_level": "medium",
                "actionable_items": [
                    "Action item 1",
                    "Action item 2"
                ],
                "customer_segment": "power_user",
                "summary": "Brief summary of the feedback"
            }}

            Guidelines:
            - Sentiment score should be between -1 (very negative) and 1 (very positive)
            - Urgency level: low, medium, high, critical
            - Customer segment: new_user, casual_user, power_user, enterprise_user
            - Focus on actionable insights for product development
            """

            # Try Gemini first, then fall back to OpenRouter
            if self.langchain_gemini:
                try:
                    response = self.langchain_gemini.invoke(prompt)
                    result_text = response
                except Exception as e:
                    logger.warning(f"Gemini failed, falling back to OpenRouter: {e}")
                    result_text = self._call_openrouter_sync(prompt)
            else:
                result_text = self._call_openrouter_sync(prompt)

            # Parse JSON response
            try:
                # Extract JSON from response if it contains extra text
                if "```json" in result_text:
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif "{" in result_text:
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    result_text = result_text[json_start:json_end]

                analysis = json.loads(result_text)

                # Validate required fields
                required_fields = [
                    "insights",
                    "sentiment_score",
                    "key_themes",
                    "summary",
                ]
                for field in required_fields:
                    if field not in analysis:
                        analysis[field] = (
                            []
                            if field != "sentiment_score" and field != "summary"
                            else (
                                0.0
                                if field == "sentiment_score"
                                else "Analysis completed"
                            )
                        )

                return analysis

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                # Return fallback structure
                return {
                    "insights": ["Transcript analyzed successfully"],
                    "sentiment_score": 0.0,
                    "key_themes": ["Customer feedback"],
                    "pain_points": [],
                    "feature_requests": [],
                    "urgency_level": "medium",
                    "actionable_items": ["Review transcript for manual analysis"],
                    "customer_segment": "casual_user",
                    "summary": "Transcript processed but detailed analysis unavailable",
                }

        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            raise

    def analyze_competitor_data(self, competitor_data: str, context: Dict) -> Dict:
        """
        Analyze competitor data using the Market Maven AI agent

        Args:
            competitor_data: The competitor information to analyze
            context: Additional context (user_id, analysis_type, etc.)

        Returns:
            Dict containing competitive intelligence analysis
        """
        try:
            # Create Market Maven analysis prompt
            prompt = f"""
            As the Market Maven agent for Define Consult, analyze the following competitor information and provide strategic competitive intelligence.

            Competitor Data:
            {competitor_data}

            Analysis Context: {context.get('analysis_type', 'general_competitor_analysis')}

            Provide a comprehensive competitive intelligence report in JSON format:
            {{
                "executive_summary": "1-2 sentence overview of key findings",
                "key_updates": [
                    {{
                        "update_type": "feature_launch|pricing_change|messaging_shift|partnership|funding",
                        "summary": "Brief description of the change",
                        "impact_level": "high|medium|low",
                        "implications": "What this means for our strategy",
                        "recommended_actions": ["specific action 1", "specific action 2"],
                        "timeline": "immediate|short_term|long_term"
                    }}
                ],
                "market_trends": [
                    {{
                        "trend": "Description of identified trend",
                        "implications": "Strategic meaning for our product"
                    }}
                ],
                "strategic_recommendations": [
                    {{
                        "priority": "high|medium|low",
                        "recommendation": "Specific strategic recommendation",
                        "rationale": "Why this is important"
                    }}
                ],
                "competitive_positioning": {{
                    "strengths": ["competitor strength 1", "competitor strength 2"],
                    "weaknesses": ["competitor weakness 1", "competitor weakness 2"],
                    "differentiation_opportunities": ["opportunity 1", "opportunity 2"]
                }},
                "threat_assessment": "high|medium|low",
                "monitoring_alerts": ["area 1 to monitor", "area 2 to monitor"],
                "confidence_level": "high|medium|low"
            }}

            Guidelines:
            - Focus on actionable insights that impact product strategy
            - Prioritize recommendations based on potential business impact
            - Be objective but provide clear strategic guidance
            - Highlight both opportunities and threats
            - Consider broader market context, not just individual moves
            """

            # Try Gemini first, then fall back to OpenRouter
            if self.langchain_gemini:
                try:
                    response = self.langchain_gemini.invoke(prompt)
                    result_text = response
                except Exception as e:
                    logger.warning(
                        f"Gemini failed for competitor analysis, falling back to OpenRouter: {e}"
                    )
                    result_text = self._call_openrouter_sync(prompt, max_tokens=1200)
            else:
                result_text = self._call_openrouter_sync(prompt, max_tokens=1200)

            # Parse JSON response
            try:
                # Extract JSON from response if it contains extra text
                if "```json" in result_text:
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif "{" in result_text:
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    result_text = result_text[json_start:json_end]

                analysis = json.loads(result_text)

                # Validate required fields
                required_fields = [
                    "executive_summary",
                    "key_updates",
                    "strategic_recommendations",
                ]
                for field in required_fields:
                    if field not in analysis:
                        if field == "executive_summary":
                            analysis[field] = (
                                "Competitive analysis completed successfully"
                            )
                        elif field in ["key_updates", "strategic_recommendations"]:
                            analysis[field] = []

                return analysis

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Market Maven AI response as JSON: {e}")
                # Return fallback structure
                return {
                    "executive_summary": "Competitor data analyzed successfully",
                    "key_updates": [
                        {
                            "update_type": "general_analysis",
                            "summary": "Competitor information processed",
                            "impact_level": "medium",
                            "implications": "Requires manual review for detailed insights",
                            "recommended_actions": [
                                "Review analysis manually",
                                "Monitor for future updates",
                            ],
                            "timeline": "short_term",
                        }
                    ],
                    "market_trends": [],
                    "strategic_recommendations": [
                        {
                            "priority": "medium",
                            "recommendation": "Conduct manual review of competitor data",
                            "rationale": "AI analysis parsing failed, human oversight needed",
                        }
                    ],
                    "competitive_positioning": {
                        "strengths": [],
                        "weaknesses": [],
                        "differentiation_opportunities": [],
                    },
                    "threat_assessment": "medium",
                    "monitoring_alerts": ["Continue monitoring competitor"],
                    "confidence_level": "low",
                }

        except Exception as e:
            logger.error(f"Error analyzing competitor data: {e}")
            raise

    def generate_content(
        self, platform: str, content_type: str, source_material: str, context: Dict
    ) -> Dict:
        """
        Generate content using the Narrative Architect AI agent

        Args:
            platform: Target platform (linkedin, twitter, medium, etc.)
            content_type: Type of content (feature_announcement, blog_post, etc.)
            source_material: The source information to transform into content
            context: Additional context for content generation

        Returns:
            Dict containing generated content and metadata
        """
        try:
            # Create Narrative Architect content generation prompt
            prompt = f"""
            As the Narrative Architect agent for Define Consult, transform the following information into compelling content.

            Platform: {platform}
            Content Type: {content_type}
            Target Audience: {context.get('target_audience', 'product managers and tech professionals')}
            Brand Tone: {context.get('brand_tone', 'professional, innovative, approachable')}

            Source Material:
            {source_material}

            Additional Context: {context.get('additional_context', '')}

            Generate engaging content optimized for {platform} with the following structure in JSON format:
            {{
                "title": "Compelling title/headline (if applicable)",
                "content": "Main content text optimized for the platform",
                "variations": [
                    {{
                        "style": "Style/approach description",
                        "content": "Content variation 1",
                        "hashtags": ["#hashtag1", "#hashtag2"],
                        "cta": "Call to action text"
                    }},
                    {{
                        "style": "Style/approach description", 
                        "content": "Content variation 2",
                        "hashtags": ["#hashtag1", "#hashtag2"],
                        "cta": "Call to action text"
                    }},
                    {{
                        "style": "Style/approach description",
                        "content": "Content variation 3", 
                        "hashtags": ["#hashtag1", "#hashtag2"],
                        "cta": "Call to action text"
                    }}
                ],
                "engagement_strategy": "Tips for maximizing engagement on {platform}",
                "visual_suggestions": "Suggested visual content or imagery",
                "posting_recommendations": "Best practices for posting this content",
                "follow_up_ideas": ["Follow-up content idea 1", "Follow-up content idea 2"]
            }}

            Platform-specific guidelines:

            LinkedIn: Professional tone, thought leadership focus, 1-3 paragraphs, business value emphasis
            Twitter: Concise and engaging, under 280 characters, conversational tone
            Medium: Detailed and educational, 3-8 paragraphs, authoritative voice
            Blog: Comprehensive and informative, problem-solution structure, SEO-friendly
            Email: Personal and direct, clear subject line, strong CTA

            Content should be:
            - Authentic and aligned with Define Consult's innovative brand
            - Value-focused for the target audience
            - Engaging and platform-optimized
            - Include clear calls to action
            - Avoid jargon unless appropriate for audience
            """

            # Try Gemini first, then fall back to OpenRouter
            if self.langchain_gemini:
                try:
                    response = self.langchain_gemini.invoke(prompt)
                    result_text = response
                except Exception as e:
                    logger.warning(
                        f"Gemini failed for content generation, falling back to OpenRouter: {e}"
                    )
                    result_text = self._call_openrouter_sync(prompt, max_tokens=1500)
            else:
                result_text = self._call_openrouter_sync(prompt, max_tokens=1500)

            # Parse JSON response
            try:
                # Extract JSON from response if it contains extra text
                if "```json" in result_text:
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif "{" in result_text:
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    result_text = result_text[json_start:json_end]

                content_result = json.loads(result_text)

                # Validate required fields
                required_fields = ["content", "variations"]
                for field in required_fields:
                    if field not in content_result:
                        if field == "content":
                            content_result[field] = "Content generated successfully"
                        elif field == "variations":
                            content_result[field] = []

                return content_result

            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse Narrative Architect AI response as JSON: {e}"
                )
                # Return fallback structure
                return {
                    "title": f"{content_type.replace('_', ' ').title()} for {platform.title()}",
                    "content": f"Generated content for {platform} - {content_type}. Source: {source_material[:100]}...",
                    "variations": [
                        {
                            "style": "Standard approach",
                            "content": f"Check out our latest update! {source_material[:100]}...",
                            "hashtags": ["#ProductManagement", "#AI", "#Innovation"],
                            "cta": "Learn more about Define Consult",
                        }
                    ],
                    "engagement_strategy": f"Optimize posting time for {platform} audience",
                    "visual_suggestions": "Include product screenshots or infographics",
                    "posting_recommendations": f"Follow {platform} best practices for maximum reach",
                    "follow_up_ideas": [
                        "Share user testimonials",
                        "Post behind-the-scenes content",
                    ],
                }

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _call_openrouter_sync(self, prompt: str, max_tokens: int = 1000) -> str:
        """Synchronous call to OpenRouter API"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://defineconsult.co",
                    "X-Title": "Define Consult",
                },
                data=json.dumps(
                    {
                        "model": "meta-llama/llama-3.1-8b-instruct:free",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                    }
                ),
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(
                    f"OpenRouter API error: {response.status_code} - {response.text}"
                )
                raise Exception(f"AI service error: {response.status_code}")

        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            raise


# User Whisperer Agent class
class UserWhispererAgent:
    """AI Agent for processing customer feedback and generating PRDs"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def process_transcript(self, transcript_content: str) -> Dict:
        """
        Process customer feedback transcript and extract insights

        Returns:
        - problem_statements: List of identified problems
        - user_stories: List of generated user stories
        - summary: Executive summary
        """

        # Step 1: Extract problem statements
        problems_prompt = f"""
        Analyze the following customer feedback transcript and extract key problem statements.
        Focus on pain points, frustrations, and unmet needs mentioned by customers.
        
        Transcript:
        {transcript_content}
        
        Please provide:
        1. A list of 3-5 core problem statements
        2. Each problem should be concise and actionable
        3. Prioritize problems by frequency mentioned and severity
        
        Format as JSON:
        {{
            "problem_statements": [
                {{
                    "title": "Brief problem title",
                    "description": "Detailed description",
                    "priority": "high|medium|low",
                    "frequency_mentioned": 3
                }}
            ]
        }}
        """

        # Generate problem statements
        problems_response = await self.ai_service.generate_completion(
            problems_prompt, max_tokens=800, temperature=0.3
        )

        # Step 2: Generate user stories
        stories_prompt = f"""
        Based on the following customer feedback, generate user stories in proper format.
        
        Customer Feedback:
        {transcript_content}
        
        Generate 5-8 user stories following this format:
        "As a [user type], I want [functionality] so that [benefit]"
        
        Include acceptance criteria for each story.
        
        Format as JSON:
        {{
            "user_stories": [
                {{
                    "title": "Story title",
                    "story": "As a... I want... so that...",
                    "acceptance_criteria": ["criteria 1", "criteria 2"],
                    "priority": "high|medium|low",
                    "estimated_effort": "small|medium|large"
                }}
            ]
        }}
        """

        stories_response = await self.ai_service.generate_completion(
            stories_prompt, max_tokens=1200, temperature=0.5
        )

        # Step 3: Generate executive summary
        summary_prompt = f"""
        Create an executive summary of the customer feedback analysis.
        
        Customer Feedback:
        {transcript_content[:1000]}...
        
        Provide:
        1. Key themes (2-3 sentences)
        2. Top priorities for product development
        3. Recommended next steps
        
        Keep it concise and actionable for product managers.
        """

        summary_response = await self.ai_service.generate_completion(
            summary_prompt, max_tokens=400, temperature=0.4
        )

        return {
            "problem_statements": problems_response,
            "user_stories": stories_response,
            "summary": summary_response,
            "status": "completed",
        }


class MarketMavenAgent:
    """AI Agent for competitive intelligence and market analysis"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def analyze_competitor_content(
        self, content: str, competitor_name: str
    ) -> Dict:
        """
        Analyze competitor website content for insights
        """

        analysis_prompt = f"""
        Analyze the following content from competitor "{competitor_name}" and provide strategic insights.
        
        Content:
        {content}
        
        Please provide:
        1. Key features or offerings mentioned
        2. Pricing strategy insights (if any)
        3. Target audience signals
        4. Positioning and messaging analysis
        5. Potential threats or opportunities for our product
        
        Format as JSON:
        {{
            "features": ["feature 1", "feature 2"],
            "pricing_insights": "analysis of pricing strategy",
            "target_audience": "identified target segments",
            "positioning": "how they position themselves",
            "threat_level": "high|medium|low",
            "opportunities": ["opportunity 1", "opportunity 2"],
            "recommended_actions": ["action 1", "action 2"]
        }}
        """

        analysis_response = await self.ai_service.generate_completion(
            analysis_prompt, max_tokens=800, temperature=0.4
        )

        return {
            "analysis": analysis_response,
            "competitor": competitor_name,
            "status": "completed",
        }


class NarrativeArchitectAgent:
    """AI Agent for content generation and product evangelism"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def generate_social_content(
        self, feature_description: str, platform: str = "linkedin"
    ) -> Dict:
        """
        Generate social media content for product features
        """

        platform_guidelines = {
            "linkedin": "Professional tone, focus on business value, 1-3 paragraphs",
            "twitter": "Concise, engaging, max 280 characters, use emojis sparingly",
            "medium": "Detailed, thought leadership style, 3-5 paragraphs",
        }

        guidelines = platform_guidelines.get(platform, platform_guidelines["linkedin"])

        content_prompt = f"""
        Create engaging social media content for {platform} about this new product feature:
        
        Feature Description:
        {feature_description}
        
        Platform Guidelines: {guidelines}
        
        Create content that:
        1. Highlights the key benefit to users
        2. Creates excitement and engagement
        3. Includes a clear call-to-action
        4. Matches the platform's tone and style
        
        Provide 3 different variations.
        
        Format as JSON:
        {{
            "platform": "{platform}",
            "variations": [
                {{
                    "content": "social media post content",
                    "hashtags": ["#hashtag1", "#hashtag2"],
                    "cta": "call to action text"
                }}
            ]
        }}
        """

        content_response = await self.ai_service.generate_completion(
            content_prompt, max_tokens=600, temperature=0.7
        )

        return {
            "content": content_response,
            "platform": platform,
            "status": "completed",
        }


# Initialize service instances
ai_service = AIService()
user_whisperer = UserWhispererAgent(ai_service)
market_maven = MarketMavenAgent(ai_service)
narrative_architect = NarrativeArchitectAgent(ai_service)
