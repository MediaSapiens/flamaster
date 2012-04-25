define [
  'chaplin/controller',
  'views/index_view', 'views/signup_view'
], (Controller, IndexView, SignUpView) ->
  'use strict'

  class PageController extends Controller

    historyURL: (options) ->
      console.log "PageController#historyURL", options
      options.path or ''

    index: -> @view = new IndexView

    signup: -> @view = new SignUpView
