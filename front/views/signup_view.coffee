define [
  'chaplin/view',
  'text!templates/sign_up.hbs'
], (View, template) ->
  'use strict'

  class SignUpView extends View

    autoRender: true
    containerSelector: "#content"
    id: "signup"
    @template = template

    initialize: ->
      super
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
      data = @serializeForm(ev.target)
      @model.save data,
        error: (model, response) => @displayErrors

    displayErrors: (model, response) ->
      if response.responseText?
        for field, message of JSON.parse(response.responseText)
          @renderError field, message
      else
        for field, message of response
          @renderError field, message


