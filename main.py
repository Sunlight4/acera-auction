from google.appengine.api import users, mail, images
from google.appengine.ext import ndb, db
import webapp2, random, pickle, urllib, datetime, locale
locale.setlocale(locale.LC_ALL, '')
class Product(ndb.Model):
    usid_owner=ndb.StringProperty()
    email_owner=ndb.StringProperty()
    name=ndb.StringProperty()
    desc=ndb.TextProperty()
    minprice=ndb.FloatProperty()
    identity=ndb.StringProperty()
    image=ndb.BlobProperty()
    tags=ndb.PickleProperty()
    inc=ndb.FloatProperty(default=0)
    end_date=ndb.DateTimeProperty()

body="""Guess what!
You have notifications on your Acera Commerce account. Better get to acera-commerce.appspot.com and check them out!
Thanks,
The Acera Commerce Team"""
class AlertBuy(ndb.Model):
    owner=ndb.StringProperty()
    product=ndb.KeyProperty()
    buyer=ndb.UserProperty()
    price=ndb.FloatProperty()
    identity=ndb.StringProperty()
    when=ndb.DateTimeProperty(auto_now_add=True)
class BeenOnServer(ndb.Model):
    email=ndb.StringProperty()
    when=ndb.DateTimeProperty(auto_now_add=True)
class AlertReminder(ndb.Model):
    to=ndb.StringProperty()
    content=ndb.StringProperty()
    identity=ndb.StringProperty()

class AlertChat(ndb.Model):
    to=ndb.StringProperty()
    sent_by=ndb.StringProperty()
    content=ndb.StringProperty()
    identity=ndb.StringProperty()
class MainPage(webapp2.RequestHandler):

    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()
        if user:
            self.response.write('''<html><head>
<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head>
<body>''')
            #Change the 0 to a 1 to begin tracking when people go on to the server
            if 0:
                b=BeenOnServer()
                b.email=user.email()
                b.put()
            if 0:
                products=Product.query().fetch(100)
                for i in products:i.key.delete()
        
               
            
            self.response.write('<span>Hello, ' + user.nickname()+'<br>')
            alert_buys=AlertBuy.query(AlertBuy.owner==user.user_id())
            if alert_buys:
                for i in alert_buys:
                    try:
                        minprice=Product.query(Product.identity==i.identity).get().minprice
                        if minprice>i.price:
                            r=AlertChat()
                            r.to=i.buyer.user_id()
                            r.sent_by=i.owner
                            content="Your offer to buy %s for %s dollars was defeated. You may need to raise your bid!" %(i.product.get().name, i.price)
                            r.content=content
                            r.put()
                            #mail.send_mail('ethans@aceraschool.org', i.buyer.email(), "Offer defeated", content)
                            continue
                        name=i.product.get().name
                        email=i.buyer.nickname()
                        price=i.price
                        self.response.write('<form action="/plusminus" method="post">A bid has been placed by '+email+" on the product "+name+" for "+str(price)+"<br>")
                        self.response.write('<input type="hidden" name="productID" value="'+i.identity+'">')
                        self.response.write('<input type="radio" name="action" value="Accept">Accept(end the auction and give the item to this person)<br>')
                        self.response.write('<input type="radio" name="action" value="Decline">Decline(remove this bid)<br>')
                        self.response.write('<input type="submit" value="Accept/Decline Offer"></form>')
                    except AttributeError:
                        try:
                            r=AlertChat()
                            r.to=i.buyer.user_id()
                            r.sent_by=i.owner
                            content="Your offer to buy %s for %s dollars was defeated. You may need to raise your bid!" %(i.product.get().name, i.price)
                            r.content=content
                            r.put()
                            #mail.send_mail('ethans@aceraschool.org', i.buyer.email(), "Offer declined", content)
                        except:
                            #i.key.delete()
                            pass
            alert_reminders=AlertReminder.query(AlertReminder.to==user.user_id()).fetch(100)
            if alert_reminders:
                for i in alert_reminders:
                    self.response.write('<b>'+i.content+'</b><br>')
            alert_chats=AlertChat.query(AlertChat.to==user.user_id()).fetch(100)
            if alert_chats:
                for i in alert_chats:
                    #self.response.write(i.content+'<br>')
                    i.key.delete()
            
                
                    
            if users.is_current_user_admin():self.response.write('<a href="/addform">Click here</a> to register a product.<br>')
            self.response.write('<a href="/scroll">Click here</a> to scroll through available products<br>')
            self.response.write('<a href="/clear">Click here</a> to clear all reminders<br>')
            self.response.write('</span></body></html>')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class ProductForm(webapp2.RequestHandler):
    def get(self):
        self.response.write('''<html><head>
<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head>
<body><form action="/register" enctype="multipart/form-data" method="post">
<div><textarea rows="1" cols="50" name="name">
Enter the name of your product here
</textarea><br></div>
<div><textarea rows="4" cols="50" name="desc">
Enter a description of your product here
</textarea><br></div>
<div>Minimum bid:
<input type="number" name="minprice"><br></div><div><label>A picture of the product:</label></div>
<div><input type="file" name="pic" accept="image/*"></div>
End date:<select name="month">
  <option value="1" selected>January</option>
  <option value="2">February</option>
  <option value="3">March</option>
  <option value="4">April</option>
  <option value="5">May</option>
  <option value="6">June</option>
  <option value="7">July</option>
  <option value="8">August</option>
  <option value="9">September</option>
  <option value="10">October</option>
  <option value="11">November</option>
  <option value="12">December</option>
</select> <input type="number" name="day"> <input type="number" name="year"> at <input type="number" name="hours">:<input type="number" name="minutes">
<div><input type="submit" value="Submit"><br></div>
</form></body></html>''')

class RegisterProduct(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()

        if user:
            name=self.request.get("name")
            desc=self.request.get("desc")
            minprice=int(self.request.get("minprice"))
            if name==None:
                self.response.write("GLITCH ON NAME FIELD!")
                return
            if desc==None:
                self.response.write("GLITCH ON DESC FIELD!")
                return
            if minprice==None:
                self.response.write("GLITCH ON MIN_PRICE FIELD!")
                return
                
            p=Product()

            p.usid_owner=user.user_id()
            p.email_owner=user.email()
            p.name=name
            p.desc=desc
            p.minprice=minprice
            p.image=db.Blob(str(self.request.get("pic")))
            p.identity=p.name+str(int(random.random()*1000))
            p.tags=self.request.get("tag")
            month=int(self.request.get("month"))
            year=int(self.request.get("year"))
            hour=int(self.request.get("hours"))
            day=int(self.request.get("day"))
            minute=int(self.request.get("minutes"))
            hour+=5 
            if hour>24:
                hour-=24
                day+=1
            p.end_date=datetime.datetime(year, month, day, hour, minute)
            p.put()
            self.redirect('/')
        
class Scroller(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        self.response.write('''<html><head>
<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head>
<body>''')
        if self.request.get("alert")=="yes":
            self.response.write("""<script>
        var x = alert("Your bid has been registered.");
        window.location.replace("/scroll");
        
        </script>""")
            #self.redirect("/scroll")
        now=datetime.datetime.utcnow()
        q=Product.query()
        if len(q.fetch(100))<=0:
            self.response.write("No products found.")
        for product in q.fetch(100):
            self.response.write('<img src="/image?productID='+urllib.quote(product.identity)+'"></img>')
            self.response.write('<form action="/placeorder" method="post"><b>'+product.name+'</b><input type="hidden" name="productID" value="'+product.identity+'"><br>')
            self.response.write(product.desc+"<br>")
            self.response.write('Owned by '+users.User(product.email_owner).nickname()+'('+product.email_owner+')'+'.<br>')
            self.response.write('''Place a bid for $<input type="text" name="price"><br><input type="submit" value="Place Bid"></form><br>''')
            try:
                bids=AlertBuy.query(AlertBuy.product==product.key).order(-AlertBuy.price, AlertBuy.identity)
                highest_bid=bids.get()
                if (highest_bid.buyer==user):
                    self.response.write("Your bid of %.2f is the highest bid.<br>" %highest_bid.price)
                else:
                    user_bids=AlertBuy.query(AlertBuy.product==product.key, AlertBuy.buyer==user).order(-AlertBuy.price, AlertBuy.identity)
                    highest_user_bid=user_bids.get()
                    if highest_user_bid==None:
                        if highest_bid==None:
                            self.response.write("No bids yet on this item. Bids must be higher than "+str(product.minprice))
                        else:self.response.write("The current highest bid is %.2f. You have not placed a bid yet on this item.<br>" %(highest_bid.price))
                    else:
                        self.response.write("Your bid of %.2f is %.2f lower than the highest bid of %.2f. Would you like to raise your bid?<br>" %(highest_user_bid.price, highest_bid.price-highest_user_bid.price, highest_bid.price)) 
                
                self.response.write('<form action="/viewbids" method="get"><input type="hidden" name="productID" value="'+product.identity+'"><input type="submit" value="View the Bid Sheet"></form><br>')
            except AttributeError:
                for i in AlertBuy.query(AlertBuy.product==product.key).order(-AlertBuy.price, AlertBuy.identity).fetch(100):
                    self.response.write("A bid has been placed for "+str(i.price)+"<br>")
            time_left=product.end_date-now
            years, days = divmod(time_left.days, 365)
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            hours-=1
            if hours<0:
                hours+=24
                days-=1
            end_date=product.end_date-datetime.timedelta(0, 0, 0, 0, 0, 5)
            self.response.write("Hurry! Only "+str(days)+" days "+str(hours)+" hours "+str(minutes)+" minutes left! (ends on "+str(end_date)+")<hr>")
                                
        self.response.write('</body></html>')

class OrderPlacer(webapp2.RequestHandler):
    def post(self):
        p=Product.query(Product.identity==self.request.get("productID")).get()
        if not p:
            self.response.write("<html><body>We are sorry. There is an error. Please try again.</body></html")
        try:
            k=p.key
            u=p.usid_owner
            e=p.email_owner
        except AttributeError:
            self.response.write("""The auction has closed on that product. <a href="/scroll">Back</a>""")
            
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))

        bids=AlertBuy.query(AlertBuy.product==p.key).order(-AlertBuy.price, AlertBuy.identity)
        highest_bid=bids.get()
        if highest_bid!=None:price=highest_bid.price
        else:price=p.minprice
        our_price=self.request.get("price").replace(",", "")
        try:
            if (float(our_price)<=price):
                self.response.write("""Your bid is lower than the %s bid of $%.2f. Please enter a bid higher than $%.2f. <a href="/scroll">Back</a>""" %(("current highest" if (highest_bid!=None) else "minimum"), price, price))
                return
        except ValueError:
            self.response.write("""Input not valid. Please enter a valid number. <a href="/scroll">Back</a>""")
            return
        #mail.send_mail('ethans@aceraschool.org', e,"Notifications",body)
        c="This email was sent to confirm your bid of %s for the product %s" %(self.request.get("price"), p.name)
        #mail.send_mail(sender='ethans@aceraschool.org', to=user.email(), body=c+""".
#Thanks for using Acera Commerce!""", subject="Offer placed")
        a=AlertBuy()
        a.owner=u
        a.buyer=user
        a.product=k
        a.price=float(our_price)
        a.identity=k.get().identity
        a.put()
        p.minprice=float(self.request.get("price"))+p.inc
        p.put()
        self.redirect('/scroll?alert=yes')
        

class PlusMinus(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
    
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        i=AlertBuy.query(AlertBuy.identity==self.request.get("productID")).get()
        a=self.request.get("action")
        if a=="Decline":
            i.key.delete()
        if a=="Accept":
            r=AlertChat()
            r.to=i.buyer.user_id()
            r.sent_by=i.owner
            content="You won the product %s with your bid of %s" %(i.product.get().name, i.price)
            r.content=content
            i.key.delete()
            r.put()
            #mail.send_mail('ethans@aceraschool.org', i.buyer.email(), "Product won", content)
            r=AlertReminder()
            r.to=i.owner
            r.content="REMINDER:%s won the product %s with his bid of %s" %(i.buyer.nickname(), i.product.get().name, i.price)
            r.put()
            r=AlertReminder()
            r.to=i.buyer.user_id()
            r.content="REMINDER:You won the product %s with your bid of %s" %(i.product.get().name, i.price)
            tag="".join(i.product.get().tags)
            if tag!="assemblyLine":
                i.product.delete()
                i.key.delete()
            r.put()
            #mail.send_mail('ethans@aceraschool.org', i.buyer.email(), "Notifications", body)
        self.redirect("/")

       
class Sweeper(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        rs=AlertReminder.query(AlertReminder.to==user.user_id()).fetch(100)
        for i in rs:
            i.key.delete()
        self.redirect('/')

class Activity(webapp2.RequestHandler):
    def get(self):
        stuff=BeenOnServer.query().fetch(500)
        self.response.write('''<html><head>
<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /></head>
<body>''')
        for i in stuff:
            u=users.User(i.email).nickname()
            d=i.when.strftime("%A, %B %d %Y")
            self.response.write(u+" was on at "+d+"<br>")
        self.response.write("</body></html>")

class GetImage(webapp2.RequestHandler):
    def get(self):
        identity=self.request.get("productID")
        p=Product.query(Product.identity==identity).get()
        if not p:
            raise Exception, "p is None with identity "+identity
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(images.resize(p.image, 256, 256))

class BidSheet(webapp2.RequestHandler):
    def get(self):
        p=Product.query(Product.identity==self.request.get("productID")).get()
        alertbuys=AlertBuy.query(AlertBuy.product==p.key).order(-AlertBuy.price, AlertBuy.identity).fetch(100)
        for a in alertbuys:
            time=a.when-datetime.timedelta(0, 0, 0, 0, 0, 5)
            self.response.write(("Bid for $%.2f by " %a.price)+a.buyer.nickname()+" at time "+str(time)+" <br>")
        self.response.write('<a href="/scroll">Back to main page</a>')

                
                
            
            

app = webapp2.WSGIApplication([
    ('/', MainPage), ("/addform", ProductForm), ('/register', RegisterProduct), ('/scroll', Scroller), ('/placeorder', OrderPlacer), ('/plusminus', PlusMinus),
    ('/clear', Sweeper), ('/activity', Activity), ('/image', GetImage), ("/viewbids", BidSheet)
], debug=True)

