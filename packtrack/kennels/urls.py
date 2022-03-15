from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    #     path('', login_required(views.kennelListView.as_view()), name='kennels'),
    #     path('mykennels',
    #          login_required(views.kennelListView.as_view(user_kennels=True)),
    #          name='mykennels'),
    #     path('profile/<str:kennel_name>', views.view_kennel,
    #          name='kennel_profile'),
    #     path('create_kennel', views.view_create_kennel, name='create_kennel'),
    #     path('post/ajax/membership_response',
    #          views.postMembershipResponse,
    #          name="post_membership_response"),
    #     path('post/ajax/membership_request',
    #          views.postMembershipRequest,
    #          name="post_membership_request"),
    #     path('post/ajax/consensus', views.postConsensus, name="post_consensus"),
    #     path('post/ajax/consensus_vote',
    #          views.postConsensusVote,
    #          name="post_consensus_vote"),
]