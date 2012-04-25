define [
  'chaplin/controller', 'chaplin/application_view',
  'controllers/navigation_controller'
], (Controller, ApplicationView, NavigationController) ->
  'use strict'

  class ApplicationController extends Controller
    historyURL: ''

    initialize: ->
      console.log "ApplicationController#initialized"
      @initApplicationView()
      @initSidebars()

    initApplicationView: ->
      new ApplicationView()

    initSidebars: ->
      new NavigationController()
      # new SidebarController()

