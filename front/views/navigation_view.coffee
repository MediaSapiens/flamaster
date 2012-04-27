define [
  'chaplin/mediator',
  'chaplin/view',
  'text!templates/navigation.hbs'
], (mediator, View, template) ->
  'use strict'

  class NavigationView extends View

    id: 'navigation'
    tagName: 'ul'
    className: "nav nav-pills"
    containerSelector: '#navigation-wrapper'
    autoRender: true
    @template = template

    initialize: ->
      super
      # mediator.publish '!showLogin'
      # global events
      @subscribeEvent 'startupController', @render
      # model events
      @modelBind 'change:routes', @render
      # user events
      @delegate 'click', '.n-signin a', @showLoginDialog

    showLoginDialog: (ev) ->
      mediator.publish '!showLogin'
      $("#login").modal show: true

