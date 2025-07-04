// supabase/functions/notificar-ticket-finalizado/index.ts

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log("Función invocada. Procesando solicitud...");

    // 1. Extraer datos del ticket
    const { record } = await req.json();
    console.log("Datos del ticket recibidos:", record);

    if (!record || !record.requester_id) {
        throw new Error("El 'record' o 'requester_id' no llegaron en la solicitud.");
    }
    const requesterId = record.requester_id;
    console.log("Buscando email para el requester_id:", requesterId);


    // 2. Crear cliente de Supabase
    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SERVICE_KEY')!
    );
    console.log("Cliente de Supabase Admin creado.");

    // 3. Obtener email del usuario
    const { data: userData, error: userError } = await supabaseAdmin
      .from('users')
      .select('email')
      .eq('id', requesterId)
      .single();

    if (userError) throw userError;
    if (!userData) throw new Error(`Usuario no encontrado para el ID: ${requesterId}`);
    
    const userEmail = userData.email;
    console.log("Email del destinatario encontrado:", userEmail);

    // 4. Enviar correo
    console.log("Intentando enviar correo de Magic Link...");
    const { data: emailData, error: emailError } = await supabaseAdmin.auth.admin.generateLink({
        type: 'magiclink',
        email: userEmail,
        options: {
            data: {
                subject: `✅ Tu ticket ha sido finalizado: #${record.id.substring(0, 8)}`,
                title: record.title,
                message: 'Nos complace informarte que tu solicitud ha sido completada por nuestro equipo.'
            }
        }
    });

    if (emailError) throw emailError;

    console.log("Llamada al servicio de correo exitosa. Respuesta:", emailData);

    return new Response(JSON.stringify({ message: `Correo procesado para ${userEmail}` }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    });

  } catch (error) {
    console.error("Error dentro de la Edge Function:", error.message);
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    });
  }
})