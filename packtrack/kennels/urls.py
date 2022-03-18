from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.view_kennels, name='kennels'),
    path('<str:name>', views.view_kennel, name='kennel'),
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