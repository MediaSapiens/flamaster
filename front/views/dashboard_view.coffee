define [
    'chaplin/view', 'text!templates/dashboard.hbs'
], (View, template) ->
  'use strict'

  class DashboardView extends View
    autoRender: true
    containerSelector: '#content'
    id: 'dashboard'
    @template: template
