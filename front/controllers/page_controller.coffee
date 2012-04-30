define [
  'chaplin/mediator', 'chaplin/controller',
  'models/user',
  'views/index_view', 'views/signup_view', 'views/dashboard_view'
], (mediator, Controller, User, IndexView, SignUpView, DashboardView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: ->
        @view = new DashboardView


    signup: ->
      nUser = User.extend urlRoot: '/account/sessions/'
      @view = new SignUpView model: new nUser

    dashboard: -> @view = new DashboardView
