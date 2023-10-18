import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice
from model_bakery import baker

# Model testing
class QuestionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        #Generating instance of Question model using baker
        cls.future_question = baker.make('polls.Question', pub_date=timezone.now() + datetime.timedelta(days=30))
        cls.old_question = baker.make('polls.Question', pub_date=timezone.now() - datetime.timedelta(days=1, seconds=1))
        cls.recent_question = baker.make('polls.Question', pub_date=timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59))
    
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        self.assertIs(self.future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        self.assertIs(self.old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        self.assertIs(self.recent_question.was_published_recently(), True)

#Choice test using baker library 

class ChoiceModelTests(TestCase):
    def test_fake_test_to_create_choice_instance(slef):
        choice = baker.make('polls.Choice', _quantity=3)
        print("Here is the list of question in choice instance")
        # print(choice.question.question_text)


# View Testing
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        time = timezone.now() + datetime.timedelta(days=-30)
        question = baker.make('polls.Question', pub_date=time)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        question = baker.make('polls.Question', pub_date=time)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        #past question
        time = timezone.now() + datetime.timedelta(days=-30)
        question = baker.make('polls.Question', pub_date=time)

        #future question
        time = timezone.now() + datetime.timedelta(days=30)
        baker.make('polls.Question', pub_date=time)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = baker.make('polls.Question', pub_date=timezone.now() + datetime.timedelta(days=-30))
        question2 = baker.make('polls.Question', pub_date=timezone.now() + datetime.timedelta(days=-5))

        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = baker.make('polls.Question', pub_date=timezone.now() + datetime.timedelta(days=5))
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = baker.make('polls.Question', pub_date=timezone.now() + datetime.timedelta(days=-5))
        # print(past_question.id)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
