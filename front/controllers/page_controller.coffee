define [
  'chaplin/controller',
  'models/user',
  'views/index_view', 'views/signup_view'
], (Controller, User, IndexView, SignUpView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: -> @view = new IndexView

    signup: ->
      nUser = User.extend urlRoot: '/account/sessions/'
      @view = new SignUpView model: new nUser
