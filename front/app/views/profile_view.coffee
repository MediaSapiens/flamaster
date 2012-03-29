{SessionModel} = require 'models/session_model'
{ProfileModel} = require 'models/profile_model'

{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  initialize: (options) ->
    @session = new SessionModel
    @model = new ProfileModel id: options.id

    @session.on 'all', (args...) =>
      console.log args

    app.homeView.getCurrentUser
      success: (model, resp) =>
        @session.set model.toJSON(), silent: true
        @model.fetch
          success: =>
            @render()

  render: ->
    baseContext = _.extend baseContext,
      username: do =>
        if @model.first_name? or @model.last_name?
          username = $.trim "#{@model.first_name} #{@model.last_name}"
        if not username? or username.length == 0
          username = @model.get 'email'
        username
    console.log @model.get 'email'
    @$el.html @template(baseContext)
    @el
