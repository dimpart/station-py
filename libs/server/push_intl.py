# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from ..utils.localizations import Translations


class PushTmpl:
    
    recv_message = 'Dear {receiver}: {sender} sent you a message.'
    recv_text = 'Dear {receiver}: {sender} sent you a text message.'
    recv_file = 'Dear {receiver}: {sender} sent you a file.'
    recv_image = 'Dear {receiver}: {sender} sent you an image.'
    recv_voice = 'Dear {receiver}: {sender} sent you a voice message.'
    recv_video = 'Dear {receiver}: {sender} sent you a video.'
    recv_page = 'Dear {receiver}: {sender} sent you a web page.'
    recv_card = 'Dear {receiver}: {sender} sent you a name card.'
    recv_money = 'Dear {receiver}: {sender} sent you some money.'
    recv_combine = 'Dear {receiver}: {sender} sent you a chat history.'

    grp_recv_message = 'Dear {receiver}: {sender} sent you a message in group "{group}".'
    grp_recv_text = 'Dear {receiver}: {sender} sent you a text message in group "{group}".'
    grp_recv_file = 'Dear {receiver}: {sender} sent you a file in group "{group}".'
    grp_recv_image = 'Dear {receiver}: {sender} sent you an image in group "{group}".'
    grp_recv_voice = 'Dear {receiver}: {sender} sent you a voice message in group "{group}".'
    grp_recv_video = 'Dear {receiver}: {sender} sent you a video in group "{group}".'
    grp_recv_page = 'Dear {receiver}: {sender} sent you a web page in group "{group}".'
    grp_recv_card = 'Dear {receiver}: {sender} sent you a name card in group "{group}".'
    grp_recv_money = 'Dear {receiver}: {sender} sent you some money in group "{group}".'
    grp_recv_combine = 'Dear {receiver}: {sender} sent you a chat history in group "{group}".'


#
#   Language Packages
#


_lang_en_US = {

    PushTmpl.recv_message: 'Dear {receiver}: {sender} sent you a message.',
    PushTmpl.recv_text: 'Dear {receiver}: {sender} sent you a text message.',
    PushTmpl.recv_file: 'Dear {receiver}: {sender} sent you a file.',
    PushTmpl.recv_image: 'Dear {receiver}: {sender} sent you an image.',
    PushTmpl.recv_voice: 'Dear {receiver}: {sender} sent you a voice message.',
    PushTmpl.recv_video: 'Dear {receiver}: {sender} sent you a video.',
    PushTmpl.recv_money: 'Dear {receiver}: {sender} sent you some money.',

    PushTmpl.grp_recv_message: 'Dear {receiver}: {sender} sent you a message in group "{group}".',
    PushTmpl.grp_recv_text: 'Dear {receiver}: {sender} sent you a text message in group "{group}".',
    PushTmpl.grp_recv_file: 'Dear {receiver}: {sender} sent you a file in group "{group}".',
    PushTmpl.grp_recv_image: 'Dear {receiver}: {sender} sent you an image in group "{group}".',
    PushTmpl.grp_recv_voice: 'Dear {receiver}: {sender} sent you a voice message in group "{group}".',
    PushTmpl.grp_recv_video: 'Dear {receiver}: {sender} sent you a video in group "{group}".',
    PushTmpl.grp_recv_money: 'Dear {receiver}: {sender} sent you some money in group "{group}".',

}


_lang_es_ES = {

    PushTmpl.recv_message: 'Estimado/a {receiver}: {sender} le envió un mensaje.',
    PushTmpl.recv_text: 'Estimado/a {receiver}: {sender} le envió un mensaje de texto.',
    PushTmpl.recv_file: 'Estimado/a {receiver}: {sender} le envió un archivo.',
    PushTmpl.recv_image: 'Estimado/a {receiver}: {sender} le envió una imagen.',
    PushTmpl.recv_voice: 'Estimado/a {receiver}: {sender} le envió un mensaje de voz.',
    PushTmpl.recv_video: 'Estimado/a {receiver}: {sender} le envió un video.',
    PushTmpl.recv_money: 'Estimado/a {receiver}: {sender} le envió algo de dinero.',

    PushTmpl.grp_recv_message: 'Estimado/a {receiver}: {sender} le envió un mensaje en el grupo "{group}".',
    PushTmpl.grp_recv_text: 'Estimado/a {receiver}: {sender} le envió un mensaje de texto en el grupo "{group}".',
    PushTmpl.grp_recv_file: 'Estimado/a {receiver}: {sender} le envió un archivo en el grupo "{group}".',
    PushTmpl.grp_recv_image: 'Estimado/a {receiver}: {sender} le envió una imagen en el grupo "{group}".',
    PushTmpl.grp_recv_voice: 'Estimado/a {receiver}: {sender} le envió un mensaje de voz en el grupo "{group}".',
    PushTmpl.grp_recv_video: 'Estimado/a {receiver}: {sender} le envió un video en el grupo "{group}".',
    PushTmpl.grp_recv_money: 'Estimado/a {receiver}: {sender} le envió algo de dinero en el grupo "{group}".',

}


_lang_fr_FR = {

    PushTmpl.recv_message: 'Cher/Chère {receiver} : {sender} vous a envoyé un message.',
    PushTmpl.recv_text: 'Cher/Chère {receiver} : {sender} vous a envoyé un message texte.',
    PushTmpl.recv_file: 'Cher/Chère {receiver} : {sender} vous a envoyé un fichier.',
    PushTmpl.recv_image: 'Cher/Chère {receiver} : {sender} vous a envoyé une image.',
    PushTmpl.recv_voice: 'Cher/Chère {receiver} : {sender} vous a envoyé un message vocal.',
    PushTmpl.recv_video: 'Cher/Chère {receiver} : {sender} vous a envoyé une vidéo.',
    PushTmpl.recv_money: 'Cher/Chère {receiver} : {sender} vous a envoyé de l\'argent.',

    PushTmpl.grp_recv_message: 'Cher/Chère {receiver} : {sender} vous a envoyé un message dans le groupe "{group}".',
    PushTmpl.grp_recv_text: 'Cher/Chère {receiver} : {sender} vous a envoyé un message texte dans le groupe "{group}".',
    PushTmpl.grp_recv_file: 'Cher/Chère {receiver} : {sender} vous a envoyé un fichier dans le groupe "{group}".',
    PushTmpl.grp_recv_image: 'Cher/Chère {receiver} : {sender} vous a envoyé une image dans le groupe "{group}".',
    PushTmpl.grp_recv_voice: 'Cher/Chère {receiver} : {sender} vous a envoyé un message vocal dans le groupe "{group}".',
    PushTmpl.grp_recv_video: 'Cher/Chère {receiver} : {sender} vous a envoyé une vidéo dans le groupe "{group}".',
    PushTmpl.grp_recv_money: 'Cher/Chère {receiver} : {sender} vous a envoyé de l\'argent dans le groupe "{group}".',

}


_lang_de_DE = {

    PushTmpl.recv_message: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Nachricht gesendet.',
    PushTmpl.recv_text: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Textnachricht gesendet.',
    PushTmpl.recv_file: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Datei gesendet.',
    PushTmpl.recv_image: 'Liebe/Lieber {receiver}: {sender} hat Ihnen ein Bild gesendet.',
    PushTmpl.recv_voice: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Sprachnachricht gesendet.',
    PushTmpl.recv_video: 'Liebe/Lieber {receiver}: {sender} hat Ihnen ein Video gesendet.',
    PushTmpl.recv_money: 'Liebe/Lieber {receiver}: {sender} hat Ihnen etwas Geld gesendet.',

    PushTmpl.grp_recv_message: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Nachricht in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_text: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Textnachricht in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_file: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Datei in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_image: 'Liebe/Lieber {receiver}: {sender} hat Ihnen ein Bild in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_voice: 'Liebe/Lieber {receiver}: {sender} hat Ihnen eine Sprachnachricht in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_video: 'Liebe/Lieber {receiver}: {sender} hat Ihnen ein Video in der Gruppe "{group}" gesendet.',
    PushTmpl.grp_recv_money: 'Liebe/Lieber {receiver}: {sender} hat Ihnen etwas Geld in der Gruppe "{group}" gesendet.',

}


_lang_it_IT = {

    PushTmpl.recv_message: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio.',
    PushTmpl.recv_text: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio di testo.',
    PushTmpl.recv_file: 'Caro/a {receiver}: {sender} ti ha inviato un file.',
    PushTmpl.recv_image: 'Caro/a {receiver}: {sender} ti ha inviato un\'immagine.',
    PushTmpl.recv_voice: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio vocale.',
    PushTmpl.recv_video: 'Caro/a {receiver}: {sender} ti ha inviato un video.',
    PushTmpl.recv_money: 'Caro/a {receiver}: {sender} ti ha inviato dei soldi.',

    PushTmpl.grp_recv_message: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio nel gruppo "{group}".',
    PushTmpl.grp_recv_text: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio di testo nel gruppo "{group}".',
    PushTmpl.grp_recv_file: 'Caro/a {receiver}: {sender} ti ha inviato un file nel gruppo "{group}".',
    PushTmpl.grp_recv_image: 'Caro/a {receiver}: {sender} ti ha inviato un\'immagine nel gruppo "{group}".',
    PushTmpl.grp_recv_voice: 'Caro/a {receiver}: {sender} ti ha inviato un messaggio vocale nel gruppo "{group}".',
    PushTmpl.grp_recv_video: 'Caro/a {receiver}: {sender} ti ha inviato un video nel gruppo "{group}".',
    PushTmpl.grp_recv_money: 'Caro/a {receiver}: {sender} ti ha inviato dei soldi nel gruppo "{group}".',

}


_lang_nl_NL = {

    PushTmpl.recv_message: 'Beste {receiver}: {sender} heeft je een bericht gestuurd.',
    PushTmpl.recv_text: 'Beste {receiver}: {sender} heeft je een tekstbericht gestuurd.',
    PushTmpl.recv_file: 'Beste {receiver}: {sender} heeft je een bestand gestuurd.',
    PushTmpl.recv_image: 'Beste {receiver}: {sender} heeft je een afbeelding gestuurd.',
    PushTmpl.recv_voice: 'Beste {receiver}: {sender} heeft je een spraakbericht gestuurd.',
    PushTmpl.recv_video: 'Beste {receiver}: {sender} heeft je een video gestuurd.',
    PushTmpl.recv_money: 'Beste {receiver}: {sender} heeft je wat geld gestuurd.',

    PushTmpl.grp_recv_message: 'Beste {receiver}: {sender} heeft je een bericht gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_text: 'Beste {receiver}: {sender} heeft je een tekstbericht gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_file: 'Beste {receiver}: {sender} heeft je een bestand gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_image: 'Beste {receiver}: {sender} heeft je een afbeelding gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_voice: 'Beste {receiver}: {sender} heeft je een spraakbericht gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_video: 'Beste {receiver}: {sender} heeft je een video gestuurd in de groep "{group}".',
    PushTmpl.grp_recv_money: 'Beste {receiver}: {sender} heeft je wat geld gestuurd in de groep "{group}".',

}


_lang_pt_PT = {

    PushTmpl.recv_message: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem.',
    PushTmpl.recv_text: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem de texto.',
    PushTmpl.recv_file: 'Caro/a {receiver}: {sender} enviou-lhe um arquivo.',
    PushTmpl.recv_image: 'Caro/a {receiver}: {sender} enviou-lhe uma imagem.',
    PushTmpl.recv_voice: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem de voz.',
    PushTmpl.recv_video: 'Caro/a {receiver}: {sender} enviou-lhe um vídeo.',
    PushTmpl.recv_money: 'Caro/a {receiver}: {sender} enviou-lhe algum dinheiro.',

    PushTmpl.grp_recv_message: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem no grupo "{group}".',
    PushTmpl.grp_recv_text: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem de texto no grupo "{group}".',
    PushTmpl.grp_recv_file: 'Caro/a {receiver}: {sender} enviou-lhe um arquivo no grupo "{group}".',
    PushTmpl.grp_recv_image: 'Caro/a {receiver}: {sender} enviou-lhe uma imagem no grupo "{group}".',
    PushTmpl.grp_recv_voice: 'Caro/a {receiver}: {sender} enviou-lhe uma mensagem de voz no grupo "{group}".',
    PushTmpl.grp_recv_video: 'Caro/a {receiver}: {sender} enviou-lhe um vídeo no grupo "{group}".',
    PushTmpl.grp_recv_money: 'Caro/a {receiver}: {sender} enviou-lhe algum dinheiro no grupo "{group}".',

}


_lang_ru_RU = {

    PushTmpl.recv_message: 'Дорогой/Дорогая {receiver}: {sender} отправил вам сообщение.',
    PushTmpl.recv_text: 'Дорогой/Дорогая {receiver}: {sender} отправил вам текстовое сообщение.',
    PushTmpl.recv_file: 'Дорогой/Дорогая {receiver}: {sender} отправил вам файл.',
    PushTmpl.recv_image: 'Дорогой/Дорогая {receiver}: {sender} отправил вам изображение.',
    PushTmpl.recv_voice: 'Дорогой/Дорогая {receiver}: {sender} отправил вам голосовое сообщение.',
    PushTmpl.recv_video: 'Дорогой/Дорогая {receiver}: {sender} отправил вам видео.',
    PushTmpl.recv_money: 'Дорогой/Дорогая {receiver}: {sender} отправил вам немного денег.',

    PushTmpl.grp_recv_message: 'Дорогой/Дорогая {receiver}: {sender} отправил вам сообщение в группе "{group}".',
    PushTmpl.grp_recv_text: 'Дорогой/Дорогая {receiver}: {sender} отправил вам текстовое сообщение в группе "{group}".',
    PushTmpl.grp_recv_file: 'Дорогой/Дорогая {receiver}: {sender} отправил вам файл в группе "{group}".',
    PushTmpl.grp_recv_image: 'Дорогой/Дорогая {receiver}: {sender} отправил вам изображение в группе "{group}".',
    PushTmpl.grp_recv_voice: 'Дорогой/Дорогая {receiver}: {sender} отправил вам голосовое сообщение в группе "{group}".',
    PushTmpl.grp_recv_video: 'Дорогой/Дорогая {receiver}: {sender} отправил вам видео в группе "{group}".',
    PushTmpl.grp_recv_money: 'Дорогой/Дорогая {receiver}: {sender} отправил вам немного денег в группе "{group}".',

}


_lang_ar = {

    PushTmpl.recv_message: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة.',
    PushTmpl.recv_text: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة نصية.',
    PushTmpl.recv_file: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} ملفًا.',
    PushTmpl.recv_image: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} صورة.',
    PushTmpl.recv_voice: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة صوتية.',
    PushTmpl.recv_video: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} فيديو.',
    PushTmpl.recv_money: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} بعض المال.',

    PushTmpl.grp_recv_message: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة في المجموعة "{group}".',
    PushTmpl.grp_recv_text: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة نصية في المجموعة "{group}".',
    PushTmpl.grp_recv_file: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} ملفًا في المجموعة "{group}".',
    PushTmpl.grp_recv_image: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} صورة في المجموعة "{group}".',
    PushTmpl.grp_recv_voice: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} رسالة صوتية في المجموعة "{group}".',
    PushTmpl.grp_recv_video: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} فيديو في المجموعة "{group}".',
    PushTmpl.grp_recv_money: 'عزيزي/عزيزتي {receiver}: أرسل لك {sender} بعض المال في المجموعة "{group}".',

}


_lang_af_ZA = {

    PushTmpl.recv_message: 'Liewe {receiver}: {sender} het vir jou \'n boodskap gestuur.',
    PushTmpl.recv_text: 'Liewe {receiver}: {sender} het vir jou \'n teksboodskap gestuur.',
    PushTmpl.recv_file: 'Liewe {receiver}: {sender} het vir jou \'n lêer gestuur.',
    PushTmpl.recv_image: 'Liewe {receiver}: {sender} het vir jou \'n beeld gestuur.',
    PushTmpl.recv_voice: 'Liewe {receiver}: {sender} het vir jou \'n stemboodskap gestuur.',
    PushTmpl.recv_video: 'Liewe {receiver}: {sender} het vir jou \'n video gestuur.',
    PushTmpl.recv_money: 'Liewe {receiver}: {sender} het vir jou \'n bietjie geld gestuur.',

    PushTmpl.grp_recv_message: 'Liewe {receiver}: {sender} het vir jou \'n boodskap in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_text: 'Liewe {receiver}: {sender} het vir jou \'n teksboodskap in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_file: 'Liewe {receiver}: {sender} het vir jou \'n lêer in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_image: 'Liewe {receiver}: {sender} het vir jou \'n beeld in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_voice: 'Liewe {receiver}: {sender} het vir jou \'n stemboodskap in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_video: 'Liewe {receiver}: {sender} het vir jou \'n video in die groep "{group}" gestuur.',
    PushTmpl.grp_recv_money: 'Liewe {receiver}: {sender} het vir jou \'n bietjie geld in die groep "{group}" gestuur.',

}


_lang_hi_IN = {

    PushTmpl.recv_message: 'प्रिय {receiver}: {sender} ने आपको एक संदेश भेजा है।',
    PushTmpl.recv_text: 'प्रिय {receiver}: {sender} ने आपको एक टेक्स्ट संदेश भेजा है।',
    PushTmpl.recv_file: 'प्रिय {receiver}: {sender} ने आपको एक फ़ाइल भेजी है।',
    PushTmpl.recv_image: 'प्रिय {receiver}: {sender} ने आपको एक छवि भेजी है।',
    PushTmpl.recv_voice: 'प्रिय {receiver}: {sender} ने आपको एक ध्वनि संदेश भेजा है।',
    PushTmpl.recv_video: 'प्रिय {receiver}: {sender} ने आपको एक वीडियो भेजा है।',
    PushTmpl.recv_money: 'प्रिय {receiver}: {sender} ने आपको कुछ पैसे भेजे हैं।',

    PushTmpl.grp_recv_message: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक संदेश भेजा है।',
    PushTmpl.grp_recv_text: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक टेक्स्ट संदेश भेजा है।',
    PushTmpl.grp_recv_file: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक फ़ाइल भेजी है।',
    PushTmpl.grp_recv_image: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक छवि भेजी है।',
    PushTmpl.grp_recv_voice: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक ध्वनि संदेश भेजा है।',
    PushTmpl.grp_recv_video: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में एक वीडियो भेजा है।',
    PushTmpl.grp_recv_money: 'प्रिय {receiver}: {sender} ने आपको समूह "{group}" में कुछ पैसे भेजे हैं।',

}


_lang_bn_BD = {

    PushTmpl.recv_message: 'প্রিয় {receiver}: {sender} আপনাকে একটি বার্তা পাঠিয়েছেন।',
    PushTmpl.recv_text: 'প্রিয় {receiver}: {sender} আপনাকে একটি টেক্সট বার্তা পাঠিয়েছেন।',
    PushTmpl.recv_file: 'প্রিয় {receiver}: {sender} আপনাকে একটি ফাইল পাঠিয়েছেন।',
    PushTmpl.recv_image: 'প্রিয় {receiver}: {sender} আপনাকে একটি ছবি পাঠিয়েছেন।',
    PushTmpl.recv_voice: 'প্রিয় {receiver}: {sender} আপনাকে একটি ভয়েস বার্তা পাঠিয়েছেন।',
    PushTmpl.recv_video: 'প্রিয় {receiver}: {sender} আপনাকে একটি ভিডিও পাঠিয়েছেন।',
    PushTmpl.recv_money: 'প্রিয় {receiver}: {sender} আপনাকে কিছু টাকা পাঠিয়েছেন।',

    PushTmpl.grp_recv_message: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি বার্তা পাঠিয়েছেন।',
    PushTmpl.grp_recv_text: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি টেক্সট বার্তা পাঠিয়েছেন।',
    PushTmpl.grp_recv_file: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি ফাইল পাঠিয়েছেন।',
    PushTmpl.grp_recv_image: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি ছবি পাঠিয়েছেন।',
    PushTmpl.grp_recv_voice: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি ভয়েস বার্তা পাঠিয়েছেন।',
    PushTmpl.grp_recv_video: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে একটি ভিডিও পাঠিয়েছেন।',
    PushTmpl.grp_recv_money: 'প্রিয় {receiver}: {sender} আপনাকে গোষ্ঠী "{group}" তে কিছু টাকা পাঠিয়েছেন।',

}


_lang_ja_JP = {

    PushTmpl.recv_message: '親愛なる{receiver}様：{sender}からメッセージが届きました。',
    PushTmpl.recv_text: '親愛なる{receiver}様：{sender}からテキストメッセージが届きました。',
    PushTmpl.recv_file: '親愛なる{receiver}様：{sender}からファイルが届きました。',
    PushTmpl.recv_image: '親愛なる{receiver}様：{sender}から画像が届きました。',
    PushTmpl.recv_voice: '親愛なる{receiver}様：{sender}からボイスメッセージが届きました。',
    PushTmpl.recv_video: '親愛なる{receiver}様：{sender}からビデオが届きました。',
    PushTmpl.recv_money: '親愛なる{receiver}様：{sender}からお金が届きました。',

    PushTmpl.grp_recv_message: '親愛なる{receiver}様：{sender}がグループ「{group}」でメッセージを送りました。',
    PushTmpl.grp_recv_text: '親愛なる{receiver}様：{sender}がグループ「{group}」でテキストメッセージを送りました。',
    PushTmpl.grp_recv_file: '親愛なる{receiver}様：{sender}がグループ「{group}」でファイルを送りました。',
    PushTmpl.grp_recv_image: '親愛なる{receiver}様：{sender}がグループ「{group}」で画像を送りました。',
    PushTmpl.grp_recv_voice: '親愛なる{receiver}様：{sender}がグループ「{group}」でボイスメッセージを送りました。',
    PushTmpl.grp_recv_video: '親愛なる{receiver}様：{sender}がグループ「{group}」でビデオを送りました。',
    PushTmpl.grp_recv_money: '親愛なる{receiver}様：{sender}がグループ「{group}」でお金を送りました。',

}


_lang_ko_KR = {

    PushTmpl.recv_message: '친애하는 {receiver}님: {sender}님이 메시지를 보냈습니다.',
    PushTmpl.recv_text: '친애하는 {receiver}님: {sender}님이 텍스트 메시지를 보냈습니다.',
    PushTmpl.recv_file: '친애하는 {receiver}님: {sender}님이 파일을 보냈습니다.',
    PushTmpl.recv_image: '친애하는 {receiver}님: {sender}님이 이미지를 보냈습니다.',
    PushTmpl.recv_voice: '친애하는 {receiver}님: {sender}님이 음성 메시지를 보냈습니다.',
    PushTmpl.recv_video: '친애하는 {receiver}님: {sender}님이 비디오를 보냈습니다.',
    PushTmpl.recv_money: '친애하는 {receiver}님: {sender}님이 일부 돈을 보냈습니다.',

    PushTmpl.grp_recv_message: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 메시지를 보냈습니다.',
    PushTmpl.grp_recv_text: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 텍스트 메시지를 보냈습니다.',
    PushTmpl.grp_recv_file: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 파일을 보냈습니다.',
    PushTmpl.grp_recv_image: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 이미지를 보냈습니다.',
    PushTmpl.grp_recv_voice: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 음성 메시지를 보냈습니다.',
    PushTmpl.grp_recv_video: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 비디오를 보냈습니다.',
    PushTmpl.grp_recv_money: '친애하는 {receiver}님: {sender}님이 그룹 "{group}"에서 일부 돈을 보냈습니다.',

}


_lang_tr_TR = {

    PushTmpl.recv_message: 'Sevgili {receiver}: {sender} size bir mesaj gönderdi.',
    PushTmpl.recv_text: 'Sevgili {receiver}: {sender} size bir metin mesajı gönderdi.',
    PushTmpl.recv_file: 'Sevgili {receiver}: {sender} size bir dosya gönderdi.',
    PushTmpl.recv_image: 'Sevgili {receiver}: {sender} size bir resim gönderdi.',
    PushTmpl.recv_voice: 'Sevgili {receiver}: {sender} size bir sesli mesaj gönderdi.',
    PushTmpl.recv_video: 'Sevgili {receiver}: {sender} size bir video gönderdi.',
    PushTmpl.recv_money: 'Sevgili {receiver}: {sender} size bir miktar para gönderdi.',

    PushTmpl.grp_recv_message: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir mesaj gönderdi.',
    PushTmpl.grp_recv_text: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir metin mesajı gönderdi.',
    PushTmpl.grp_recv_file: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir dosya gönderdi.',
    PushTmpl.grp_recv_image: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir resim gönderdi.',
    PushTmpl.grp_recv_voice: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir sesli mesaj gönderdi.',
    PushTmpl.grp_recv_video: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir video gönderdi.',
    PushTmpl.grp_recv_money: 'Sevgili {receiver}: {sender} "{group}" grubunda size bir miktar para gönderdi.',

}


_lang_ms_MY = {

    PushTmpl.recv_message: 'Hormat {receiver}: {sender} menghantar anda mesej.',
    PushTmpl.recv_text: 'Hormat {receiver}: {sender} menghantar anda mesej teks.',
    PushTmpl.recv_file: 'Hormat {receiver}: {sender} menghantar anda fail.',
    PushTmpl.recv_image: 'Hormat {receiver}: {sender} menghantar anda imej.',
    PushTmpl.recv_voice: 'Hormat {receiver}: {sender} menghantar anda mesej suara.',
    PushTmpl.recv_video: 'Hormat {receiver}: {sender} menghantar anda video.',
    PushTmpl.recv_money: 'Hormat {receiver}: {sender} menghantar anda sedikit wang.',

    PushTmpl.grp_recv_message: 'Hormat {receiver}: {sender} menghantar anda mesej dalam kumpulan "{group}".',
    PushTmpl.grp_recv_text: 'Hormat {receiver}: {sender} menghantar anda mesej teks dalam kumpulan "{group}".',
    PushTmpl.grp_recv_file: 'Hormat {receiver}: {sender} menghantar anda fail dalam kumpulan "{group}".',
    PushTmpl.grp_recv_image: 'Hormat {receiver}: {sender} menghantar anda imej dalam kumpulan "{group}".',
    PushTmpl.grp_recv_voice: 'Hormat {receiver}: {sender} menghantar anda mesej suara dalam kumpulan "{group}".',
    PushTmpl.grp_recv_video: 'Hormat {receiver}: {sender} menghantar anda video dalam kumpulan "{group}".',
    PushTmpl.grp_recv_money: 'Hormat {receiver}: {sender} menghantar anda sedikit wang dalam kumpulan "{group}".',

}


_lang_th_TH = {

    PushTmpl.recv_message: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความถึงคุณ',
    PushTmpl.recv_text: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความทางข้อความถึงคุณ',
    PushTmpl.recv_file: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งไฟล์ถึงคุณ',
    PushTmpl.recv_image: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งรูปถึงคุณ',
    PushTmpl.recv_voice: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความเสียงถึงคุณ',
    PushTmpl.recv_video: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งวิดีโอถึงคุณ',
    PushTmpl.recv_money: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งเงินถึงคุณ',

    PushTmpl.grp_recv_message: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_text: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความทางข้อความในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_file: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งไฟล์ในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_image: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งรูปในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_voice: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งข้อความเสียงในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_video: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งวิดีโอในกลุ่ม "{group}" ถึงคุณ',
    PushTmpl.grp_recv_money: 'เรียน {receiver} ที่เป็นที่รัก: {sender} ส่งเงินในกลุ่ม "{group}" ถึงคุณ',

}


_lang_id_ID = {

    PushTmpl.recv_message: 'Halo {receiver}: {sender} mengirimkan pesan kepada Anda.',
    PushTmpl.recv_text: 'Halo {receiver}: {sender} mengirimkan pesan teks kepada Anda.',
    PushTmpl.recv_file: 'Halo {receiver}: {sender} mengirimkan file kepada Anda.',
    PushTmpl.recv_image: 'Halo {receiver}: {sender} mengirimkan gambar kepada Anda.',
    PushTmpl.recv_voice: 'Halo {receiver}: {sender} mengirimkan pesan suara kepada Anda.',
    PushTmpl.recv_video: 'Halo {receiver}: {sender} mengirimkan video kepada Anda.',
    PushTmpl.recv_money: 'Halo {receiver}: {sender} mengirimkan sejumlah uang kepada Anda.',

    PushTmpl.grp_recv_message: 'Halo {receiver}: {sender} mengirimkan pesan dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_text: 'Halo {receiver}: {sender} mengirimkan pesan teks dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_file: 'Halo {receiver}: {sender} mengirimkan file dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_image: 'Halo {receiver}: {sender} mengirimkan gambar dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_voice: 'Halo {receiver}: {sender} mengirimkan pesan suara dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_video: 'Halo {receiver}: {sender} mengirimkan video dalam grup "{group}" kepada Anda.',
    PushTmpl.grp_recv_money: 'Halo {receiver}: {sender} mengirimkan sejumlah uang dalam grup "{group}" kepada Anda.',

}


_lang_vi_VN = {

    PushTmpl.recv_message: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn.',
    PushTmpl.recv_text: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn văn bản.',
    PushTmpl.recv_file: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tệp tin.',
    PushTmpl.recv_image: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một hình ảnh.',
    PushTmpl.recv_voice: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn giọng nói.',
    PushTmpl.recv_video: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một video.',
    PushTmpl.recv_money: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một số tiền.',

    PushTmpl.grp_recv_message: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn trong nhóm "{group}".',
    PushTmpl.grp_recv_text: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn văn bản trong nhóm "{group}".',
    PushTmpl.grp_recv_file: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tệp tin trong nhóm "{group}".',
    PushTmpl.grp_recv_image: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một hình ảnh trong nhóm "{group}".',
    PushTmpl.grp_recv_voice: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một tin nhắn giọng nói trong nhóm "{group}".',
    PushTmpl.grp_recv_video: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một video trong nhóm "{group}".',
    PushTmpl.grp_recv_money: 'Kính gửi {receiver}: {sender} đã gửi cho bạn một số tiền trong nhóm "{group}".',

}


_lang_zh_CN = {

    PushTmpl.recv_message: '亲爱的{receiver}：{sender} 给您发送了一条消息。',
    PushTmpl.recv_text: '亲爱的{receiver}：{sender} 给您发送了一条文本消息。',
    PushTmpl.recv_file: '亲爱的{receiver}：{sender} 给您发送了一个文件。',
    PushTmpl.recv_image: '亲爱的{receiver}：{sender} 给您发送了一张图片。',
    PushTmpl.recv_voice: '亲爱的{receiver}：{sender} 给您发送了一条语音消息。',
    PushTmpl.recv_video: '亲爱的{receiver}：{sender} 给您发送了一段视频。',
    PushTmpl.recv_money: '亲爱的{receiver}：{sender} 给您发送了一些钱。',

    PushTmpl.grp_recv_message: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一条消息。',
    PushTmpl.grp_recv_text: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一条文本消息。',
    PushTmpl.grp_recv_file: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一个文件。',
    PushTmpl.grp_recv_image: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一张图片。',
    PushTmpl.grp_recv_voice: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一条语音消息。',
    PushTmpl.grp_recv_video: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一段视频。',
    PushTmpl.grp_recv_money: '亲爱的{receiver}：{sender} 在群组“{group}”中给您发送了一些钱。',

}

_lang_zh_TW = {

    PushTmpl.recv_message: '親愛的{receiver}：{sender} 寄了一封訊息給您。',
    PushTmpl.recv_text: '親愛的{receiver}：{sender} 寄了一則文字訊息給您。',
    PushTmpl.recv_file: '親愛的{receiver}：{sender} 寄了一個檔案給您。',
    PushTmpl.recv_image: '親愛的{receiver}：{sender} 寄了一張圖片給您。',
    PushTmpl.recv_voice: '親愛的{receiver}：{sender} 寄了一段語音訊息給您。',
    PushTmpl.recv_video: '親愛的{receiver}：{sender} 寄了一段影片給您。',
    PushTmpl.recv_money: '親愛的{receiver}：{sender} 寄了一些錢給您。',

    PushTmpl.grp_recv_message: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一封訊息給您。',
    PushTmpl.grp_recv_text: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一則文字訊息給您。',
    PushTmpl.grp_recv_file: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一個檔案給您。',
    PushTmpl.grp_recv_image: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一張圖片給您。',
    PushTmpl.grp_recv_voice: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一段語音訊息給您。',
    PushTmpl.grp_recv_video: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一段影片給您。',
    PushTmpl.grp_recv_money: '親愛的{receiver}：{sender} 在群組「{group}」中寄了一些錢給您。',

}


#
#   Set Dictionaries
#

Translations.set_dictionary(dictionary=_lang_af_ZA, locale='af')
Translations.set_dictionary(dictionary=_lang_af_ZA, locale='af_ZA')  # Afrikaans-South Africa

Translations.set_dictionary(dictionary=_lang_ar, locale='ar')  # Arabic-Modern Standard Arabic

Translations.set_dictionary(dictionary=_lang_bn_BD, locale='bn')
Translations.set_dictionary(dictionary=_lang_bn_BD, locale='bn_BD')  # Bengali-Bangladesh

Translations.set_dictionary(dictionary=_lang_de_DE, locale='de')
Translations.set_dictionary(dictionary=_lang_de_DE, locale='de_DE')  # German-Germany

Translations.set_dictionary(dictionary=_lang_en_US, locale='en')
Translations.set_dictionary(dictionary=_lang_en_US, locale='en_US')
Translations.set_dictionary(dictionary=_lang_en_US, locale='en_GB')

Translations.set_dictionary(dictionary=_lang_es_ES, locale='es')
Translations.set_dictionary(dictionary=_lang_es_ES, locale='es_ES')  # Spanish-Spain

Translations.set_dictionary(dictionary=_lang_fr_FR, locale='fr')
Translations.set_dictionary(dictionary=_lang_fr_FR, locale='fr_FR')  # French-France

Translations.set_dictionary(dictionary=_lang_hi_IN, locale='hi')
Translations.set_dictionary(dictionary=_lang_hi_IN, locale='hi_IN')  # Hindi-North India

Translations.set_dictionary(dictionary=_lang_id_ID, locale='id')
Translations.set_dictionary(dictionary=_lang_id_ID, locale='id_ID')  # Indonesian-Indonesia

Translations.set_dictionary(dictionary=_lang_it_IT, locale='it')
Translations.set_dictionary(dictionary=_lang_it_IT, locale='it_IT')  # Italian-Italy

Translations.set_dictionary(dictionary=_lang_ja_JP, locale='ja')
Translations.set_dictionary(dictionary=_lang_ja_JP, locale='ja_JP')  # Japanese-Japan

Translations.set_dictionary(dictionary=_lang_ko_KR, locale='ko')
Translations.set_dictionary(dictionary=_lang_ko_KR, locale='ko_KR')  # Korean-Korea

Translations.set_dictionary(dictionary=_lang_tr_TR, locale='tr')
Translations.set_dictionary(dictionary=_lang_tr_TR, locale='tr_TR')  # Turkish-Turkey

Translations.set_dictionary(dictionary=_lang_ms_MY, locale='ms')
Translations.set_dictionary(dictionary=_lang_ms_MY, locale='ms_MY')  # Malaysian-Malaysia

Translations.set_dictionary(dictionary=_lang_nl_NL, locale='nl')
Translations.set_dictionary(dictionary=_lang_nl_NL, locale='nl_NL')  # Dutch-Netherlands

Translations.set_dictionary(dictionary=_lang_pt_PT, locale='pt')
Translations.set_dictionary(dictionary=_lang_pt_PT, locale='pt_PT')  # Portuguese-Portugal

Translations.set_dictionary(dictionary=_lang_ru_RU, locale='ru')
Translations.set_dictionary(dictionary=_lang_ru_RU, locale='ru_RU')  # Russian-Russia

Translations.set_dictionary(dictionary=_lang_th_TH, locale='th')
Translations.set_dictionary(dictionary=_lang_th_TH, locale='th_TH')  # Thai-Thailand

Translations.set_dictionary(dictionary=_lang_vi_VN, locale='vi')
Translations.set_dictionary(dictionary=_lang_vi_VN, locale='vi_VN')  # Vietnamese-Vietnam

Translations.set_dictionary(dictionary=_lang_zh_CN, locale='zh')
Translations.set_dictionary(dictionary=_lang_zh_CN, locale='zh_CN')
Translations.set_dictionary(dictionary=_lang_zh_TW, locale='zh_TW')
