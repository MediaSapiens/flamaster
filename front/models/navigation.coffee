define [
  'chaplin/mediator', 'chaplin/model'
], (mediator, Model) ->
  'use strict'

  class Navigation extends Model
    defaults:
      routes: []

    initialize: ->
      super
      @subscribeEvent 'loginStatus', @updateRoutes
      @updateRoutes()

    updateRoutes: =>
      @set
        routes: [
          {id: 'index', path: '', title: 'Index'}
        ]
      routes = @get 'routes'

      unless mediator.user?
        routes.push {id: 'signin', path: 'signin', title: 'Sign In'},
          {id: 'signup', path: 'signup', title: 'Sign Up'}

      else
        routes.push {id: 'signout', path: 'signout', title: 'Sign Out'}
