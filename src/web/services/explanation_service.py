from typing import Optional
from dataclasses import dataclass

from domain.models.problem import Problem
from domain.repositories.problems import ProblemRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.user_problem_rating import UserProblemRatingRepository
from application.recommenders.base import RecommendationResult


@dataclass
class RecommendationExplanation:
    main_reason: str
    details: list[str]
    similar_problems: list[str]
    tags_improvement: list[str]


class ExplanationService:
    def __init__(
        self,
        problem_repository: ProblemRepository,
        user_problem_status_repository: UserProblemStatusRepository,
        submission_repository: SubmissionRepository,
        user_problem_rating_repository: UserProblemRatingRepository,
    ):
        self.problem_repository = problem_repository
        self.user_problem_status_repository = user_problem_status_repository
        self.submission_repository = submission_repository
        self.user_problem_rating_repository = user_problem_rating_repository

    async def explain_recommendation(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        recommender_type: str,
    ) -> RecommendationExplanation:
        problem = None
        if recommendation["contest_id"] and recommendation["problem_index"]:
            problem = await self.problem_repository.find_by_contest_and_index(
                recommendation["contest_id"], recommendation["problem_index"]
            )

        if recommender_type == "content_based":
            return await self._explain_content_based(user_id, recommendation, problem)
        elif recommender_type == "collaborative":
            return await self._explain_collaborative(user_id, recommendation, problem)
        elif recommender_type == "rating_based":
            return await self._explain_rating_based(user_id, recommendation, problem)
        elif recommender_type == "hybrid":
            return await self._explain_hybrid(user_id, recommendation, problem)
        elif recommender_type == "matrix_factorization":
            return await self._explain_matrix_factorization(
                user_id, recommendation, problem
            )
        else:
            return RecommendationExplanation(
                main_reason="Рекомендована на основе вашего профиля",
                details=[],
                similar_problems=[],
                tags_improvement=[],
            )

    async def _explain_content_based(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        problem: Optional[Problem],
    ) -> RecommendationExplanation:
        solved_statuses = (
            await self.user_problem_status_repository.find_solved_by_user_id(user_id)
        )

        similar_problems: list[str] = []
        tags_improvement: list[str] = []

        if problem and problem.tags:
            tags_improvement = problem.tags[:3]

            for status in solved_statuses[:5]:
                if not status.contest_id or not status.problem_index:
                    continue

                solved_problem = (
                    await self.problem_repository.find_by_contest_and_index(
                        status.contest_id, status.problem_index
                    )
                )

                if solved_problem and solved_problem.tags:
                    common_tags = set(problem.tags) & set(solved_problem.tags)
                    if common_tags:
                        problem_name = (
                            solved_problem.name
                            or f"{status.contest_id}{status.problem_index}"
                        )
                        similar_problems.append(problem_name)

        main_reason = "Похожа на задачи, которые вы уже решали"
        if tags_improvement:
            main_reason += f" (теги: {', '.join(tags_improvement[:3])})"

        details = []
        if problem and problem.rating:
            details.append(f"Рейтинг задачи: {problem.rating}")

        if recommendation["score"] > 0.7:
            details.append("Высокая степень соответствия вашему профилю")

        return RecommendationExplanation(
            main_reason=main_reason,
            details=details,
            similar_problems=similar_problems[:3],
            tags_improvement=tags_improvement,
        )

    async def _explain_collaborative(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        problem: Optional[Problem],
    ) -> RecommendationExplanation:
        main_reason = "Решена пользователями, похожими на вас"

        details = []
        if problem and problem.rating:
            details.append(f"Рейтинг задачи: {problem.rating}")

        details.append("Рекомендована на основе collaborative filtering")

        return RecommendationExplanation(
            main_reason=main_reason,
            details=details,
            similar_problems=[],
            tags_improvement=problem.tags if problem else [],
        )

    async def _explain_rating_based(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        problem: Optional[Problem],
    ) -> RecommendationExplanation:
        ratings = []
        if recommendation["contest_id"] and recommendation["problem_index"]:
            ratings = await self.user_problem_rating_repository.find_by_problem(
                recommendation["contest_id"], recommendation["problem_index"]
            )

        avg_usefulness = 0.0
        avg_interest = 0.0
        avg_quality = 0.0
        count = 0

        for rating in ratings:
            if rating.usefulness_rating:
                avg_usefulness += rating.usefulness_rating
            if rating.interest_rating:
                avg_interest += rating.interest_rating
            if rating.quality_rating:
                avg_quality += rating.quality_rating
            count += 1

        if count > 0:
            avg_usefulness /= count
            avg_interest /= count
            avg_quality /= count

        main_reason = "Высоко оценена сообществом"
        if avg_usefulness > 0:
            main_reason += f" (полезность: {avg_usefulness:.1f}/5)"

        details = []
        if avg_interest > 0:
            details.append(f"Интересность: {avg_interest:.1f}/5")
        if avg_quality > 0:
            details.append(f"Качество: {avg_quality:.1f}/5")
        if problem and problem.rating:
            details.append(f"Рейтинг задачи: {problem.rating}")

        return RecommendationExplanation(
            main_reason=main_reason,
            details=details,
            similar_problems=[],
            tags_improvement=problem.tags if problem else [],
        )

    async def _explain_hybrid(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        problem: Optional[Problem],
    ) -> RecommendationExplanation:
        content_explanation = await self._explain_content_based(
            user_id, recommendation, problem
        )
        collaborative_explanation = await self._explain_collaborative(
            user_id, recommendation, problem
        )

        main_reason = "Рекомендована на основе комбинации методов"
        details = [
            content_explanation.main_reason,
            collaborative_explanation.main_reason,
        ]

        if problem and problem.rating:
            details.append(f"Рейтинг задачи: {problem.rating}")

        return RecommendationExplanation(
            main_reason=main_reason,
            details=details,
            similar_problems=content_explanation.similar_problems,
            tags_improvement=content_explanation.tags_improvement,
        )

    async def _explain_matrix_factorization(
        self,
        user_id: int,
        recommendation: RecommendationResult,
        problem: Optional[Problem],
    ) -> RecommendationExplanation:
        main_reason = "Подходит вашему профилю на основе матричной факторизации"

        details = []
        if problem and problem.rating:
            details.append(f"Рейтинг задачи: {problem.rating}")

        details.append("Рекомендована с использованием ML-модели")

        return RecommendationExplanation(
            main_reason=main_reason,
            details=details,
            similar_problems=[],
            tags_improvement=problem.tags if problem else [],
        )
