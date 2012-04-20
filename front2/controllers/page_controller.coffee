define [
  'chaplin/controller',
  'views/index_view', 'views/signin_view', 'views/signup_view'
], (Controller, IndexView, SignInView, SignUpView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: -> @view = new IndexView

    signin: -> @view = new SignInView

    signup: -> @view = new SignUpView
