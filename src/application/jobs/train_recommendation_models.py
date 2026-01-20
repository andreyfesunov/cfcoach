from application.services.recommendation_service import RecommendationService


class TrainRecommendationModelsJob:
    def __init__(self, recommendation_service: RecommendationService):
        self.recommendation_service = recommendation_service

    async def execute(self) -> None:
        try:
            for recommender in self.recommendation_service.recommenders.values():
                if await recommender.needs_training():
                    await recommender.train()
        except Exception as e:
            import logging

            logging.error(f"Failed to train recommendation models: {e}")
