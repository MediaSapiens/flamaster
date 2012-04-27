define [
  'chaplin/view',
  'text!templates/navigation.hbs'
], (View, template) ->
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
      # global events
      @subscribeEvent 'startupController', @render
      # model events
      @modelBind 'change:routes', @render
      # user events
      @delegate 'click', '.n-signin a', @showLoginDialog

    showLoginDialog: (ev) ->
      console.log ev
      $("#dialogs #login").modal show: true
