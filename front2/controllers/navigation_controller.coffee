define [
  'chaplin/controller',
  'models/navigation', 'views/navigation_view'
], (Controller, Navigation, NavigationView) ->
  'use strict'

  class NavigationController extends Controller
    initialize: ->
      @model = new Navigation()
      @view = new NavigationView model: @model
      super


