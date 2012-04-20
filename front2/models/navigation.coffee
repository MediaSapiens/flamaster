define [
  'chaplin/mediator', 'chaplin/model'
], (mediator, Model) ->
  'use strict'

  class Navigation extends Model
    defaults:
      routes: [
        {id: 'index', path: '', title: 'Index'}
      ]

    initialize: ->
      super
      @subscribeEvent 'loginStatus', @updateRoutes
      @updateRoutes()

    updateRoutes: =>
      routes = @get 'routes'

      unless mediator.user?
        routes.push {id: 'signin', path: 'signin', title: 'Sign In'},
                     {id: 'signup', path: 'signup', title: 'Sign Up'}

      else
        routes.push {id: 'signout', path: 'signout', title: 'Sign Out'}
