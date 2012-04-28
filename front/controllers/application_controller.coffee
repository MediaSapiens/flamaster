define [
  'chaplin/mediator', 'chaplin/controller', 'chaplin/application_view',
  'controllers/navigation_controller'
], (mediator, Controller, ApplicationView, NavigationController) ->
  'use strict'

  class ApplicationController extends Controller
    historyURL: ''

    initialize: ->
      console.log "ApplicationController#initialized"

      @initApplicationView()
      @initSidebars()

      @subscribeEvent 'loginStatus', @loginStatus

    initApplicationView: ->
      new ApplicationView()

    initSidebars: ->
      new NavigationController()
      # new SidebarController()

    loginStatus: (loggedIn) ->
      # console.debug 'ApplicationController#loginStatus'
      mediator.router.route('/dashboard') if loggedIn

