define [
  'chaplin/view',
  'text!templates/sign_up.hbs', 'text!templates/sign_up_complete.hbs'
], (View, template, templateComplete) ->
  'use strict'

  class SignUpView extends View

    autoRender: true
    containerSelector: "#content"
    id: "signup"
    @template = template

    initialize: ->
      super
      console.log @template
      @delegate 'submit', "#sigup-form", @signUp

    getTemplateData: ->
      data =
        form:
          id: 'sigup-form'
          method: 'post'
          action: '.'
      data

    signUp: (ev) =>
      @preventDefault(ev)
      @clearErrors()

      @model.save @serializeForm(ev.target),
        success: (model, data) =>
          console.log "SignUpView#signUp", data
          @constructor.template = templateComplete
          @render()
        error: @displayErrors

