class exports.ProfileModel extends Backbone.Model
  urlRoot: '/account/profiles/'

  initialize: ->
    @front =
      edit: "/#!/profile/#{@id}/edit"
    true

  getUsername: ->
    if @first_name? or @last_name?
      username = $.trim "#{@first_name} #{@last_name}"
    if not username? or username.length == 0
      username = "please, fill your profile data"
    username
